#!/usr/bin/env python3
"""
The commandline startup script
"""
import os
import sys
import argparse

sys.path.insert(0, '.')  # noqa

from clay.core import meta
from clay.playback.player import get_player
import clay.ui.urwid as urwid
import clay.ui.gtk as gtk


player = get_player()  # pylint: disable=invalid-name


class MultilineVersionAction(argparse.Action):
    """
    An argparser action for multiple lines so we can display the copyright notice
    Based on: https://stackoverflow.com/a/41147122
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")

        self.prog = os.path.basename(sys.argv[0])
        super(MultilineVersionAction, self).__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        parser.exit(message=meta.COPYRIGHT_MESSAGE)


def main():
    """
    Starts the main clay process
    """
    try:
        from setproctitle import setproctitle
    except ImportError:
        pass
    else:
        setproctitle('clay')

    parser = argparse.ArgumentParser(
        prog=meta.APP_NAME,
        description=meta.DESCRIPTION,
        epilog="This project is neither affiliated nor endorsed by Google."
    )

    parser.add_argument("-v", "--version", action=MultilineVersionAction)
    # parser.add_argument("--osd", action='store_true', nargs=1,
    # help="Disabling or enabling desktop notifications")
    # osd_group = parser.add_mutually_exclusive_group()

    # osd_group.add_argument(
    #     "--enable-osd",
    #     help="enable sending desktop notifications",
    #     action="store_true")

    # osd_group.add_argument(
    #     "--disable-osd",
    #     help="disable sending desktop notifications",
    #     action="store_true"
    # )

    # player_group = parser.add_mutually_exclusive_group()

    # player_group.add_argument(
    #     "--mpv",
    #     help="play tracks of using the MPV player",
    #     action="store_true"
    # )

    # player_group.add_argument(
    #     "--vlc",
    #     help="Play tracks of using the VLC player",
    #     action="store_true"
    # )

    args = parser.parse_args()

    # osd.ENABLED = args.enable_osd or args.disable_osd

    if args.version:
        exit(0)

    gtk.main()


if __name__ == '__main__':
    main()
