#!/usr/bin/python
# -*- coding: utf-8 -*-
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt

from StreamHandler import StreamHandler

class Player(object):
    def __init__(self,):
        self.streamHandler = StreamHandler()
        
    def play(self, url):
        try:
            self.close()
        except:
            pass
        self.streamHandler.play(url)

    def close(self):
        self.streamHandler.close()

