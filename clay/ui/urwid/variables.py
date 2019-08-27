# This file is part of Clay.
# Copyright (C) 2018, Andrew Dunbai & Clay Contributors
#
# Clay is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Clay is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Clay. If not, see <https://www.gnu.org/licenses/>.
"""
A file containing various static variables
"""
from enum import Enum
from clay.core import settings_manager


class States(Enum):
    """
    The states taken the song
    """
    idle = 0
    loading = 1
    playing = 2
    paused = 3


class Icons:
    """
    Icons used to indicate the state, rating or how explicit a song is.
    """
    _unicode = settings_manager.get('unicode', 'clay_settings')
    state = [' ', u'\u2505', u'\u25B6', u'\u25A0']

    if _unicode:
        ratings = [' ', '\U0001F593', '\U0001F593', '\U0001F593', '\U0001F593', '\U0001F592']
        explicit = [' ', u'\U0001F174', ' ', '']
    else:
        ratings = [' ', '-', '2', '3', '4', '+']
        explicit = [' ', '[E]', ' ', ' ']
