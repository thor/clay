from clay.core import gp
from clay.playback.player import get_player
from gi.repository import Gtk, GLib

from .general import SongItem, AbstractPage

player = get_player()


class LibraryPage(AbstractPage):
    def __init__(self):
        AbstractPage.__init__(self, sorting_func=lambda song: song.title)
        gp.get_all_tracks_async(callback=lambda *args: GLib.idle_add(self.populate, *args))

    def refresh(self):
        """
        What to do when the library page reaches the top of the page.
        """
        # TODO: Maybe reload the songs in the library?
        pass

    def _activated(self, list_box, row, *args):
        track = row.get_children()[0]
        player.append_to_queue(track._track)
