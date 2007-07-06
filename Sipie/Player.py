#!/usr/bin/python
# -*- coding: utf-8 -*-
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt


from Factory import Factory, LoginError, AuthError, InvalidStream


class Player(Factory):

    def setPlayer(self,streamHandler):
        self.streamHandler = streamHandler
    
    def play(self):
        try:
            self.close()
        except:
            pass
        self.streamHandler.setURL(self.asxURL)
        self.streamHandler.play()

    def mute(self):
        self.streamHandler.mute()

    def pause(self):
        self.streamHandler.pause()

    def close(self):
        self.streamHandler.close()

