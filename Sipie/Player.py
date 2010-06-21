#!/usr/bin/python
# -*- coding: utf-8 -*-
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt


from Factory import Factory, LoginError, AuthError, InvalidStream
from StreamHandler import StreamHandler

class Player(Factory):
    def __init__(self,):
        super(Player, self).__init__()
        self.streamHandler = StreamHandler()
        
    def play(self):
        try:
            self.close()
        except:
            pass
        self.streamHandler.setURL(self.asxURL)
        self.streamHandler.play()

    def close(self):
        self.streamHandler.close()

