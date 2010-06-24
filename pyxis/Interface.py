#!/usr/bin/python
#Pyxis and Original Sipie: Sirius Command Line Player
#Copyright (C) Corey Ling, Eli Criffield
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

from Config import Config
from Player import Player
from Sirius import Sirius
import sys 
import os 
import time
import atexit
import readline
#Import with conditions
display = True
try:
    os.environ['DISPLAY']
except:
    display = False
if display:
    import pynotify

class Completer(object):
    def __init__(self, words):
        self.words = words
        self.prefix = None
        self.matching_words = []
    
    def complete(self, prefix, index):
        if prefix != self.prefix:
            self.matching_words = [
                w for w in self.words if w.startswith(prefix)
                ]
            self.prefix = prefix
        try:
            return self.matching_words[index]
        except IndexError:
            return None

class Interface(object):
    def __init__(self, opts, station):
        try:
            os.remove('debug.log')
        except OSError:
            pass
        
        self.histfile = None
        self.config = Config()
        
        self.sirius = Sirius()
        self.player = Player()
        self.options = opts

        atexit.register(self.onExit)

        if opts.list:
            self.list()
            sys.exit(0)

        if opts.setup:
            self.setup()
            sys.exit(0)

        if station != None:
            self.play(station)
        else:
            self.repl()

    def userPrompt(self):
        while True:
            try:
                userinput = raw_input("\npyxis: ").strip()
            except (EOFError, KeyboardInterrupt):
                sys.exit(0)

            if userinput.lower() == 'list':
                self.list()
                continue
            if userinput.lower() == 'exit':
                sys.exit(0)

            self.play(userinput)

    def onExit(self):
       try:
           readline.write_history_file(self.histfile)
       except:
           pass
       try:
           self.player.close()
       except:
           pass

    def play(self, stream):
        try:
            self.sirius.setStreamByLongName(stream)
        except:
            print "Invalid station name. Type 'list' to see available station names"
            return

        url = self.sirius.getAsxURL()

        self.player.play(url)
        while True: #playing loop
            playing = self.sirius.nowPlaying()
            if playing['new'] :
                if not self.options.quiet:
                    print playing['logfmt']
                if display and pynotify.init("Pyxis"):
                    n = pynotify.Notification("Sirius", playing['logfmt'][15:],
                            sys.path[0] + "/Pyxis/data/dog_white_outline.svg")
                    n.show()
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                break

    def repl(self):
        self.histfile = os.path.join(self.config.confpath,"history")

        completer = Completer([x['longName'] for x in self.sirius.getStreams()])
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer.complete)
        # Remove space as a valid word delimiter, since stream
        # names have spaces in them.
        readline.set_completer_delims(readline.get_completer_delims().strip(' '))

        try:
            readline.read_history_file(self.histfile)
        except IOError:
            pass

        print "\nWelcome to Pyxis."
        print "Enter the name of the station you want to listen to, type 'list' to see available stations or 'exit' to close the program."

        self.userPrompt()

    def list(self):
        station_cat = 'none'
        for x in self.sirius.getStreams():
            if station_cat != x['categoryKey']:
                station_cat = x['categoryKey']
                print '\n' + '\033[1m' + '[' + station_cat.replace('cat','').capitalize() + ']' + '\033[0;0m'
            print x['longName'].title()
        print ''

    def setup(self):
        self.config.create()
