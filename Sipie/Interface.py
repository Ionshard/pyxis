#!/usr/bin/python
# -*- coding: utf-8 -*-
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt
from Config import Config
from Player import Player
import StreamHandler
import sys 
import os 
import time
import atexit
#Import with conditions
haveReadline = True
try:
    import readline
except ImportError:
    haveReadline = False
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

class Interface():
    def __init__(self, opts, station):
        try:
            os.remove('debug.log')
        except:
            pass
        self.streamHandler = StreamHandler.mplayerHandler()
        self.config = Config()
        self.sipie = Player(self.config.items())
        self.sipie.setPlayer(self.streamHandler)
        atexit.register(self.onExit)
        self.options = opts

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

    def ask4Stream(self):
        try:
            stream = raw_input("\nsipie: ")
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        else:
            stream = stream.strip()

        #print 'ask4Stream "%s"'%stream #DEBUG
        return stream

    def onExit(self):
       try:
           readline.write_history_file(self.histfile)
       except:
           pass
       try:
           sipie.close()
       except:
           pass

    def play(self, stream):
        try:
            self.sipie.setStreamByLongName(stream)
        except:
            print "Invalid Station Name"
            return

        self.sipie.play()
        while True: #playing loop
            playing = self.sipie.nowPlaying()
            if playing['new'] :
                if not self.options.quiet:
                    print playing['logfmt']
                if display and pynotify.init("Sipie"):
                    n = pynotify.Notification("Sirius", playing['logfmt'][15:], sys.path[0] + "/Sipie/data/dog_white_outline.svg")
                    n.show()
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                break

    def repl(self):
        self.histfile = os.path.join(self.sipie.configpath,"history")

        if haveReadline:
            completer = Completer([x['longName'] for x in self.sipie.getStreams()])
            readline.parse_and_bind("tab: complete")
            readline.set_completer(completer.complete)
            # Remove space as a valid word delimiter, since stream
            # names have spaces in them.
            readline.set_completer_delims(readline.get_completer_delims().strip(' '))

            try:
                readline.read_history_file(self.histfile)
            except IOError:
                pass

        print "\nWelcome to Sipie."
        print "Enter the name of the station you want to listen to, type 'list' to see available stations or 'exit' to close the program."

        while True: #repl loop
            stream = self.ask4Stream()
            if stream.lower() == 'list':
                self.list()
                continue
            if stream.lower() == 'exit':
                sys.exit(0)

            self.play(stream)

    def list(self):
        station_cat = 'none'
        for x in self.sipie.getStreams():
            if station_cat != x['categoryKey']:
                station_cat = x['categoryKey']
                print '\n' + '\033[1m' + '[' + station_cat.replace('cat','').capitalize() + ']' + '\033[0;0m'
            print x['longName'].title()
        print ''

    def setup(self):
        config = Config()
        config.cliCreate()
