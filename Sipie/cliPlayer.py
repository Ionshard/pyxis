#!/usr/bin/python
# -*- coding: utf-8 -*-
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt

def cliPlayer():
    from Config import Config
    from Player import Player
    import StreamHandler
    import sys 
    import os 
    import time
    import atexit

    global histfile, readline, sipie

    haveReadline = True
    try:
        import readline
    except ImportError:
        haveReadline = False
        
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
            stream = raw_input("Enter stream: ")
        except (EOFError, KeyboardInterrupt):
            print "Thanks for playing"
            sys.exit(0)
        return stream

    def onExit():
       #global histfile, readline, sipie
       try:
           readline.write_history_file(histfile)
       except:
           pass
       sipie.close()

    if sys.platform == 'win32':
        win = True
        configdir = '.'
        streamHandler = StreamHandler.wmpHandler(
                          'c:\Program Files\Windows Media Player\mplayer2.exe')
    else:
        win = False
        configdir = '%s/.sipie'%os.environ['HOME']
        streamHandler = StreamHandler.mplayerHandler('/usr/bin/mplayer')

    histfile = os.path.join(configdir,"history")
    config = Config(configdir)
    sipie = Player(config.items())
    sipie.setPlayer(streamHandler)
    atexit.register(onExit)

    if haveReadline:
        completer = Completer(sipie.getStreams())
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
        elif sys.argv[0].lower().find("sipie") == -1 and FirstLoop:
            stream = os.path.basename(sys.argv[0])
        else:
            stream = ask4Stream()
        if stream == 'list':
            for str in sipie.getStream():
                print str
                break
        try:
            sipie.setStream(stream)
        except : #FIXME
            FirstLoop = False
            print "Invalid Stream"
            continue
        #print sipie.asxURL
        sipie.play()

        while True:
            playing = sipie.nowPlaying()
            if playing['new'] :
                print playing['logfmt']
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                break
        FirstLoop = False
