
import threading
import urllib3

from gi.repository import Gtk, Pango, GLib, Gio
from gi.repository.GdkPixbuf import Pixbuf, InterpType


class SongItem(Gtk.Grid):
    def __init__(self, track):
        Gtk.Grid.__init__(self, hexpand=True, halign=Gtk.Align.START, margin=10)
        self._track = track

        # Download the album url and resize it to fit the screen
        # TODO: Caching
        self.image = Gtk.Image()
        if track.album_url is not None and track.album_url != '':
            thread = threading.Thread(target=self._fetch_image)
            thread.daemon = True
            thread.start()
        else:
            # TODO: better icon
            self.image.set_from_stock(Gtk.STOCK_MISSING_IMAGE, Gtk.IconSize.DIALOG)

        minutes = track.duration // (1000 * 60)
        seconds = (track.duration // 1000) % 60
        self.title = Gtk.Label(label=track.title, halign=Gtk.Align.START, margin_left=5, wrap=True,
                               wrap_mode=Pango.WrapMode.CHAR)
        self.bottom = Gtk.Label(halign=Gtk.Align.START, margin_left=5, wrap=True,
                                label="{} • {:02d}:{:02d}".format(track.artist, minutes, seconds))

        self.attach(self.image, 0, 0, 1, 2)  # left, top, width, height
        self.attach(self.title, 1, 0, 2, 1)
        self.attach(self.bottom, 1, 1, 1, 1)
        self.show_all()

    def _fetch_image(self):
        http = urllib3.PoolManager()
        image = http.request('GET', self._track.album_url, preload_content=False)

        istream = Gio.MemoryInputStream.new_from_data(image.read(), None)
        pixbuf = Pixbuf.new_from_stream(istream, None)

        def _callback():
            self.image.set_from_pixbuf(pixbuf.scale_simple(50, 50, InterpType.BILINEAR))
            image.release_conn()
            self.image.show()

        GLib.idle_add(_callback)


class AbstractPage(Gtk.ScrolledWindow):
    """
    A generic class that implements basic features for all pages that contain songs.

    Args:
       initial_fetch: the amount of songs you want to fetch on load
       step: the amount songs you want to add when you reach the end
       sorting_func: a function containing one argument which sorts the tracks
    """
    def __init__(self, initial_fetch=100, step=100, sorting_func=lambda x: x):
        Gtk.ScrolledWindow.__init__(self)

        self._song_list = Gtk.ListBox()
        self._song_list.connect('row_activated', self._activated)

        self._index = self._initial_fetch = initial_fetch
        self._step = step
        self._index = initial_fetch
        self._sorting_func = sorting_func

        self.connect('edge-overshot', self._edge_reached)
        self.add(self._song_list)

    def _edge_reached(self, window, pos):
        """
        What to do whenever the edge of the list is reached.  Typically
        this just calls the `refresh` or `load_more functions` in the
        child's class.

        Args:
          window: the window that received the signal
          pos: the edge that was reached.
        """
        if pos == Gtk.PositionType.TOP:
            self.refresh()
        elif pos == Gtk.PositionType.BOTTOM:
            self.load_more()
        else:
            print("[warning]: unknown edge reached: %s" % pos)

    def _activated(self, list_box, row, *args):
        """
        What to do when a song is clicked on

        Args:
           list_box: the box with the numbers in them
           row: the song clicked on
           args: other argument passed in

        Exception:
           Throws an exception if it is not implemented in the inheriting class

        Returns:
          Nothing
        """
        raise NotImplementedError("Not Implemented")

    def _add_songs(self, tracks):
        """
        The songs you want to add to the list

        Args:
          tracks: the tracks you want to load

        """
        for track in tracks:
            songitem = SongItem(track)
            self._song_list.add(songitem)

        self._index += self._step

    def populate(self, tracks, error):
        """
        Populate the list with the provided tracks or display the error

        Args:
          tracks: the tracks you want to show
          error: the error you want to display

        Returns:
          Nothing
        """
        self._tracks = sorted(tracks, key=self._sorting_func)
        self._add_songs(self._tracks[0:self._initial_fetch])

    def refresh(self):
        """
        Refreshes the songs in the list.

        Exception:
          Raises the NotImplementedError if not implemented in the inheriting class
        """
        raise NotImplementedError()

    def load_more(self):
        """
        Loads more songs from the network.
        """
        self._add_songs(self._tracks[self._index:self._index + self._step])
        self._index += self._step
