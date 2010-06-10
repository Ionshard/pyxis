#!/usr/bin/python
# -*- coding: utf-8 -*-
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt

import Sipie
import time

#This is the directory the config files will be
config = Sipie.Config('/home/ecriffield/.sipie/')

# There's a class for mplayer xine and windows media player
# Also gstream in gnome, but haven't tested it
streamHandler = Sipie.mplayerHandler('/usr/bin/mplayer')

sipie = Sipie.Player(config.items())
sipie.setPlayer(streamHandler)

# pick a stream, you can see all avalibe with sipie.getStreams()
sipie.setStream('faction')
#Play it
sipie.play()
time.sleep(30)

# Hey whats playing on the stream i selected?
print sipie.nowPlaying()['logfmt']

time.sleep(30)

sipie.close()
