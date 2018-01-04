from random import randint

import json

from clay import vlc
from clay.eventhook import EventHook
from clay.notifications import NotificationArea
from clay.hotkeys import hotkey_manager


class Queue(object):
    def __init__(self):
        self.random = False
        self.repeat_one = False

        self.tracks = []
        self.current_track = None

    def load(self, tracks, current_track=None):
        self.tracks = tracks[:]
        if current_track is None and len(self.tracks):
            current_track = 0
        self.current_track = current_track

    def append(self, track):
        self.tracks.append(track)

    def remove(self, track):
        if track not in self.tracks:
            return

        index = self.tracks.index(track)
        self.tracks.remove(track)
        if index < self.current_track:
            self.current_track -= 1

    def get_current_track(self):
        if self.current_track is None:
            return None
        return self.tracks[self.current_track]

    def next(self, force=False):
        if self.current_track is None:
            if not len(self.tracks):
                return None
            self.current_track = self.tracks[0]

        if self.repeat_one and not force:
            return self.get_current_track()

        if self.random:
            self.current_track = randint(0, len(self.tracks) - 1)
            return self.get_current_track()

        self.current_track += 1
        if (self.current_track + 1) >= len(self.tracks):
            self.current_track = 0

        return self.get_current_track()

    def get_tracks(self):
        return self.tracks


class Player(object):
    media_position_changed = EventHook()
    media_state_changed = EventHook()
    track_changed = EventHook()
    playback_flags_changed = EventHook()
    queue_changed = EventHook()
    track_appended = EventHook()
    track_removed = EventHook()

    def __init__(self):
        self.mp = vlc.MediaPlayer()

        self.mp.event_manager().event_attach(
            vlc.EventType.MediaPlayerPlaying,
            self._media_state_changed
        )
        self.mp.event_manager().event_attach(
            vlc.EventType.MediaPlayerPaused,
            self._media_state_changed
        )
        self.mp.event_manager().event_attach(
            vlc.EventType.MediaPlayerEndReached,
            self._media_end_reached
        )
        self.mp.event_manager().event_attach(
            vlc.EventType.MediaPlayerPositionChanged,
            self._media_position_changed
        )

        hotkey_manager.play_pause += self.play_pause
        hotkey_manager.next += self.next
        hotkey_manager.prev += lambda: self.seek_absolute(0)

        self.queue = Queue()

    def broadcast_state(self):
        track = self.queue.get_current_track()
        if track is None:
            data = dict(
                playing=False,
                artist=None,
                title=None,
                progress=None,
                length=None
            )
        else:
            data = dict(
                playing=self.is_playing,
                artist=track.artist,
                title=track.title,
                progress=self.get_play_progress_seconds(),
                length=self.get_length_seconds()
            )
        with open('/tmp/clay.json', 'w') as f:
            f.write(json.dumps(data, indent=4))

    def _media_state_changed(self, e):
        self.broadcast_state()
        self.media_state_changed.fire(self.is_playing)

    def _media_end_reached(self, e):
        self.next()

    def _media_position_changed(self, e):
        self.broadcast_state()
        self.media_position_changed.fire(
            self.get_play_progress()
        )

    def load_queue(self, data, current_index=None):
        self.queue.load(data, current_index)
        self.queue_changed.fire()
        self._play()

    def append_to_queue(self, track):
        self.queue.append(track)
        self.track_appended.fire(track)
        # self.queue_changed.fire()

    def remove_from_queue(self, track):
        self.queue.remove(track)
        self.queue_changed.fire()
        self.track_removed.fire(track)

    def create_station_from_track(self, track):
        self._create_station_notification = NotificationArea.notify('Creating station...')
        track.create_station(callback=self._create_station_from_track_ready)

    def _create_station_from_track_ready(self, station, error):
        if error:
            self._create_station_notification.update('Failed to create station: {}'.format(str(error)))
            return

        if not station.get_tracks():
            self._create_station_notification.update('Newly created station is empty :(')
            return

        self.load_queue(station.get_tracks())
        self._create_station_notification.update('Station ready!')

    def get_is_random(self):
        return self.queue.random

    def get_is_repeat_one(self):
        return self.queue.repeat_one

    def set_random(self, value):
        self.queue.random = value
        self.playback_flags_changed.fire()

    def set_repeat_one(self, value):
        self.queue.repeat_one = value
        self.playback_flags_changed.fire()

    def get_queue(self):
        return self.queue.get_tracks()

    def _play(self):
        track = self.queue.get_current_track()
        if track is None:
            return
        track.get_url(callback=self._play_ready)
        self.broadcast_state()
        self.track_changed.fire(track)

    def _play_ready(self, url, error, track):
        if error:
            NotificationArea.notify('Failed to request media URL: {}'.format(str(error)))
            return
        self.mp.set_media(vlc.Media(url))
        self.mp.play()

    @property
    def is_playing(self):
        return self.mp.get_state() == vlc.State.Playing

    def play_pause(self):
        if self.is_playing:
            self.mp.pause()
        else:
            self.mp.play()

    def get_play_progress(self):
        return self.mp.get_position()

    def get_play_progress_seconds(self):
        return int(self.mp.get_position() * self.mp.get_length() / 1000)

    def get_length_seconds(self):
        return int(self.mp.get_length() // 1000)

    def next(self, force=False):
        self.queue.next(force)
        self._play()

    def get_current_track(self):
        return self.queue.get_current_track()

    # def prev(self):
    #     self.queue.prev()
    #     self._play()

    def seek(self, delta):
        self.mp.set_position(self.get_play_progress() + delta)

    def seek_absolute(self, position):
        self.mp.set_position(position)


player = Player()

