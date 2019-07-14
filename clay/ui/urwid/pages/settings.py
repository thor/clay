"""
Components for "Settings" page.
"""
import urwid

from .page import AbstractPage
from clay.core import settings_manager
from clay.playback.player import get_player
from clay.ui.urwid import hotkey_manager


player = get_player()


class SettingsPage(urwid.Columns, AbstractPage):
    """
    Settings page.
    """
    @property
    def name(self):
        return 'Settings'

    @property
    def key(self):
        return 9

    @property
    def slug(self):
        """
        Return page ID (str).
        """
        return "settings"

    def __init__(self, app):
        self.app = app
        self.username = urwid.Edit(
            edit_text=settings_manager.get('username', 'play_settings') or ''
        )
        self.password = urwid.Edit(
            mask='*', edit_text=settings_manager.get('password', 'play_settings') or ''
        )
        self.device_id = urwid.Edit(
            edit_text=settings_manager.get('device_id', 'play_settings') or ''
        )
        self.download_tracks = urwid.CheckBox(
            'Download tracks before playback',
            state=settings_manager.get('download_tracks', 'play_settings') or False
        )
        super(SettingsPage, self).__init__([urwid.ListBox(urwid.SimpleListWalker([
            urwid.Text('Settings'),
            urwid.Divider(' '),
            urwid.Text('Username'),
            urwid.AttrWrap(self.username, 'input', 'input_focus'),
            urwid.Divider(' '),
            urwid.Text('Password'),
            urwid.AttrWrap(self.password, 'input', 'input_focus'),
            urwid.Divider(' '),
            urwid.Text('Device ID'),
            urwid.AttrWrap(self.device_id, 'input', 'input_focus'),
            urwid.Divider(' '),
            self.download_tracks,
            urwid.Divider(' '),
            urwid.AttrWrap(urwid.Button(
                'Save', on_press=self.on_save
            ), 'input', 'input_focus')
        ]))])

    def on_save(self, *_):
        """
        Called when "Save" button is pressed.
        """
        with settings_manager.edit() as config:
            if 'play_settings' not in config:
                config['play_settings'] = {}
            config['play_settings']['username'] = self.username.edit_text
            config['play_settings']['password'] = self.password.edit_text
            config['play_settings']['device_id'] = self.device_id.edit_text
            config['play_settings']['download_tracks'] = self.download_tracks.state

        self.app.set_page('library')
        self.app.log_in()

    def activate(self):
        hotkey_manager.filtering = True
