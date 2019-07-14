"""
A GTK representation of a queue.
"""

from gi.repository import Gtk, GLib
from clay.playback.player import get_player
from .pages.general import SongItem

player = get_player()


class QueueItem(SongItem):
    """
    A slightly modified version of the SongItem class for songs in a queue
    """
    def __init__(self, *args):
        SongItem.__init__(self, *args)


class CurrentSongItem(SongItem):
    """
    A modified version of the SongItem class to display what song is currently being played
    """
    def __init__(self, *args):
        SongItem.__init__(self, *args)


class Queue:
    def __init__(self, tracks=[]):
        self._queue = tracks
        self._current = None

    @property
    def current_track(self):
        if not self._current or self._queue == []:
            return None
        elif not self._current:
            self._current = self._queue[0]
        return self._current

    def add_song(self, track):
        """
        Adds a song to the queue

        Args:
          track (`ui.gtk.pages.general.SongItem`): the track you want to add
        """
        player.append_to_queue(track._track)
        self._queue.append(track)

    def next(self):
        """
        Goes to the next song in the queue
        """
        self._current = player.next()

    def previous(self):
        """
        Goes to the previous song in the queue
        """
        self._current = player.prev()


queue = Queue()
