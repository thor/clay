from gi.repository import Gtk, GLib
from .pages.general import SongItem
from clay.playback.player import get_player
from .queue import queue


player = get_player()


class CurrentSongItem(SongItem):
    """
    A modified version of the SongItem class to display what song is currently being played
    """
    def __init__(self, *args):
        SongItem.__item__(self, *args)


class ActionBox(Gtk.ButtonBox):
    """
    A box containing the buttons to control clay
    """
    play_icon = Gtk.Image.new_from_icon_name("media-playback-start", Gtk.IconSize.LARGE_TOOLBAR)
    pause_icon = Gtk.Image.new_from_icon_name("media-playback-pause", Gtk.IconSize.LARGE_TOOLBAR)

    def __init__(self):
        Gtk.ButtonBox.__init__(self, Gtk.Orientation.HORIZONTAL)

        self._random_button = self._create_button("media-playlist-repeat", Gtk.ToggleButton)
        self._previous_button = self._create_button("media-skip-backward")
        self._play_button = self._create_button("media-playback-start")
        self._next_button = self._create_button("media-skip-forward")
        self._shuffle_button = self._create_button("media-playlist-shuffle", Gtk.ToggleButton)
        self._volume_button = Gtk.VolumeButton.new()

        self._random_button.connect('clicked', lambda *_: player.shuffle != player.shuffle)
        self._previous_button.connect('clicked', lambda *_: queue.previous())
        self._play_button.connect('clicked', self._play_button_clicked)
        self._next_button.connect('clicked', lambda *_: queue.next())
        self._shuffle_button.connect('clicked', lambda *_: player.repeat_queue != player.repeat_queue)

    def _play_button_clicked(self, *args):
        """
        What to do when the play button is pressed
        """
        player.play_pause()
        if player.playing:
            self._play_button.set_image(self.play_icon)
        else:
            self._play_button.set_image(self.pause_icon)

    def _create_button(self, icon, button_f=Gtk.Button):
        """
        A helper function to create a button

        Args:
          icon: the XDG compliant name for an icon
        """
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.LARGE_TOOLBAR)
        button = button_f.new()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_image(image)
        self.add(button)
        return button


class PlayBar(Gtk.Box):
    """
    A bar containing the information about Clay and the currently playing song
    """
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self._current_song = None
        self._progressbar = Gtk.ProgressBar.new()
        self._actionbox = ActionBox()

        player.media_position_changed += self._wrap(self._update_progressbar)
        player.track_changed += self._wrap(self._update_song)

        self.pack_end(self._actionbox, True, True, 0)
        self.pack_end(self._progressbar, True, True, 0)

    def _wrap(self, func):
        """
        Wrap a function as a callback so we don't overload GTK.
        """
        return lambda *args: GLib.idle_add(func, *args)

    def _update_progressbar(self, *_):
        """
        Update the progressbar that keeps track of the position in the song
        """
        self._progressbar.set_fraction(player.play_progress)

    def _update_song(self, *_):
        if self._current_song:
            self.remove(self._current_song)

        print(queue.current_track)
        self._current_song = queue.current_track
        self.pack_start(self._current_song, True, True, 0)
