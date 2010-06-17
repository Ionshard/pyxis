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

def run(opts, station):
    repl()

class Completer:
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

def ask4Stream():
    try:
        stream = raw_input("\nsipie: ")
        stream = stream.strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)
    #print 'ask4Stream "%s"'%stream #DEBUG
    return stream

def onExit():
   global histfile, readline, sipie
   try:
       readline.write_history_file(histfile)
   except:
       pass
   try:
       sipie.close()
   except:
       pass

def repl():
    global histfile, readline, sipie

        
    try:
        os.remove('debug.log')
    except:
        pass
    configdir = '%s/.sipie'%os.environ['HOME']
    streamHandler = StreamHandler.mplayerHandler('/usr/bin/mplayer')
    histfile = os.path.join(configdir,"history")
    config = Config(configdir)
    sipie = Player(config.items())
    sipie.setPlayer(streamHandler)
    atexit.register(onExit)

    if haveReadline:
        completer = Completer([x['longName'] for x in sipie.getStreams()])
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer.complete)
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass

    FirstLoop = True
    while True:
        if len(sys.argv) == 2 and FirstLoop:
            stream = sys.argv[1].lower()
            try:
		sipie.setStreamByLongName(stream)
	    except:
		print "Unable to find station: " + stream
		sys.exit(0)
        elif sys.argv[0].lower().find("sipie") == -1 and FirstLoop:
            stream = os.path.basename(sys.argv[0])
            sipie.setStreamByChannel(stream)
        else:
	  print "\nWelcome to Sipie."
	  print "Enter the name of the station you want to listen to, type 'list' to see available stations or 'exit' to close the program."
          stream = ask4Stream()
          if stream.lower() == 'list':
            for str in [x['longName'] for x in sipie.getStreams()]:
              print str
            continue
	  if stream.lower() == 'exit':
	    sys.exit(0)
          try:
              sipie.setStreamByLongName(stream)
          except : #FIXME
              FirstLoop = False
              print "Invalid Station Name"
              continue
        sipie.play()

        while True:
            playing = sipie.nowPlaying()
            if playing['new'] :
                print playing['logfmt']
                if display and pynotify.init("Sipie"):
                    n = pynotify.Notification("Sirius", playing['logfmt'][15:], sys.path[0] + "/Sipie/data/notify.png")
                    n.show()
            pass
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                break
        FirstLoop = False
