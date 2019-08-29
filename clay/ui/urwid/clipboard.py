"""
Clipboard utils.
"""
import shlex, subprocess
from clay.core import settings_manager
from clay.ui.urwid.notifications import notification_area

cmd = settings_manager.get('copy_command', 'clay_settings')
COMMAND = shlex.split(cmd) if cmd is not None else None


def copy(text):
    """
    Copy text to clipboard.

    Return True on success.
    """
    try:
        if COMMAND is None:
            return
        proc = subprocess.Popen(COMMAND, stdin=subprocess.PIPE)
        proc.communicate(text.encode('utf-8'))
    except FileNotFoundError:
        notification_area.notify(
            'Failed to copy text to clipboard. '
            'Please install "%s"' % COMMAND[0])
    except Exception as e:
        notification_area.notify(
            'Failed to copy text to clipboard. '
            'Unknown error: "%s".' % e)
