#!/usr/bin/env python

import os
import Sipie

player = Sipie.gtkPlayer
try:
    os.environ['DISPLAY']
except:
   player = Sipie.cliPlayer

try:
    player()
except:
    if player is not Sipie.cliPlayer:
        Sipie.cliPlayer()

