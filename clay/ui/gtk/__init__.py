import sys
import threading
import gi

# pylint: disable=wrong-import-position
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '0.0')

from gi.repository import Gtk, Handy, GObject
from clay.core import gp, settings_manager
from clay.playback.player import get_player

from .pages import library
from .playbar import PlayBar


player = get_player()


class Content(Handy.Leaflet):
    def __init__(self, app):
        self._app = app
        Handy.Leaflet.__init__(self, name="HdyLeaflet")

        [self.bind_property(prop, app._sidebar, prop, GObject.BindingFlags(1 | 2)) for prop in
         ("child-transition-duration", "child-transition-type", "mode-transition-type")]
          #"visible-child-name")]

        self._show_content = Gtk.Button.new_with_label("Show content")
        self._show_content.set_halign(Gtk.Align.CENTER)
        self._show_content.set_vexpand_set(False)
        self._show_content.set_property("margin", 12)

        self._play_button = Gtk.Button.new_with_label("Play + Pause")
        self._play_button.set_vexpand_set(False)
        self._play_button.set_property('margin', 12)
        self._play_button.connect('clicked', lambda *args: player.play_pause())
        self._sidebar = Gtk.ListBox()
        self._sidebar.add(self._show_content)
        self._sidebar.add(self._play_button)

        self._separator = Gtk.Separator()
        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self._content.pack_start(library.LibraryPage(), True, True, 0)
        self._content.pack_end(PlayBar(), False, True, 0)

        self._app.size_groups['sidebar'].add_widget(self._sidebar)
        self._app.size_groups['separator'].add_widget(self._separator)
        self._app.size_groups['content'].add_widget(self._content)

        self.add(self._sidebar)
        self.add(self._separator)
        self.add(self._content)

    def goto_sidebar(self):
        """
        Goto the sidebar
        """
        self.set_visible_child(self._sidebar)

    def goto_content(self):
        """
        Goto content
        """
        self.set_visible_child(self._content)


class Sidebar(Handy.Leaflet):
    """
    test
    """
    def __init__(self, app):
        Handy.Leaflet.__init__(self, child_transition_type="slide", mode_transition_type="slide",
                               name="header")
        self._app = app

        self._sidebar_header = Gtk.HeaderBar(name="sidebar_header", title="GTK+ Clay Player",
                                             show_close_button=False)
        self._separator = Gtk.Separator()
        self._content_header = Gtk.HeaderBar(name="content_header", hexpand=True, show_close_button=True)

        self._app.size_groups['sidebar'].add_widget(self._sidebar_header)
        self._app.size_groups['separator'].add_widget(self._separator)
        self._app.size_groups['content'].add_widget(self._content_header)

        self._revealer = Gtk.Revealer(reveal_child=True)
        self._revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self._button = Gtk.Button.new_from_icon_name("go-previous-symbolic", 1)
        self._revealer.add(self._button)

        self.bind_property("folded", self._revealer, "reveal-child", GObject.BindingFlags(2))
        self._revealer.bind_property("transition-duration", self,
                                     "mode-transition-duration", GObject.BindingFlags(1 | 2))

        self._content_header.add(self._revealer)

        self.add(self._sidebar_header)
        self.add(self._separator)
        self.add(self._content_header)

    def goto_content(self):
        """
        Goto the content page
        """
        self.set_visible_child(self._content_header)

    def goto_sidebar(self):
        """
        Goto sidebar
        """
        self.set_visible_child(self._sidebar_header)


class ClayGtk(Gtk.Window):
    def __init__(self):
        """
        Initialize clay
        """
        Gtk.Window.__init__(self, name="glay", title="Clay Player GTK")
        self.size_groups = {'sidebar': Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                            'content': Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                            'separator': Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                            'general': Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)}

        self.set_size_request(360, 450)

        self._titlebar = Handy.TitleBar(name="sidebar")
        self._sidebar = Sidebar(self)
        self._content = Content(self)

        self._titlebar.add(self._sidebar)

        self._content._show_content.connect('clicked', self._on_content)
        self._sidebar._button.connect('clicked', self._on_back)
        self.size_groups['general'].add_widget(self._titlebar)
        self.size_groups['general'].add_widget(self._content)

        self.set_titlebar(self._titlebar)
        self.add(self._content)
        self.show_all()

        self.connect("destroy", Gtk.main_quit)
        self.log_in()

    def _on_content(self, *args):
        """
        pass
        """
        #player.play_pause()
        self._content.goto_content()
        self._sidebar.goto_content()

    def _on_back(self, *args):
        """
        pass
        """
        self._content.goto_sidebar()
        self._sidebar.goto_sidebar()

    def log_in(self, use_token=True):
        """
        Request user authorization
        """
        authtoken, device_id, username, password = [
            settings_manager.get(key, "play_settings")
            for key
            in ('authtoken', 'device_id', 'username', 'password')
        ]

        if use_token and authtoken:
            gp.use_authtoken_async(
                authtoken,
                device_id,
                callback=self.on_check_authtoken
            )
        elif username and password and device_id:
            gp.login_async(
                username,
                password,
                device_id,
                callback=self.on_login
            )
        else:
            pass
        print("Logged in")

    def on_check_authtoken(self, success, error):
        pass

    def on_login(self, success, error):
        pass


def main():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    window = ClayGtk()
    Gtk.main()
    #window.start()
