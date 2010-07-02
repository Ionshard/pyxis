#!/usr/bin/python
#Pyxis
#Copyright (C) Corey Ling
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from Config import Config, toBool
import os
from shutil import rmtree

def logfile(file, data):
    """Log data to file"""

    if not __debugging():
        return

    filename = os.path.join(__debugDir(), file)
    dbfd = open(filename, 'w')
    dbfd.write(data)
    dbfd.close()

def log(data):
    """Append data to debug.log file"""

    if not __debugging():
        return

    filename = os.path.join(__debugDir(), 'debug.log')
    dbfd = open(filename, 'a')
    dbfd.write('%s\n' % data)
    dbfd.close()

def cleanDebug():
    """Remove old debug information"""
    global __dir, __debug
    __dir = None
    __debug = None
    try:
        rmtree(__debugDir())
    except:
        pass

def __debugDir():
    global __dir

    if __dir == None:
        config = Config()
        settings = config.debug
        __dir = settings.directory
        __dir = os.path.expanduser(__dir)

    if not os.path.exists(__dir):
        os.makedirs(__dir)

    return __dir

def __debugging():
    global __debug
    if __debug == None:
        config = Config()
        __debug = toBool(config.debug.debug)

    return __debug
