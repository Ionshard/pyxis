#!/usr/bin/env python
# Eli Criffield

import os
import sys
import Sipie

player = Sipie.wxPlayer
try:
    os.environ['DISPLAY']
except:
   Sipie.cliPlayer()
   sys.exit(0)

try:
    player()
except:
    try:
        Sipie.gtkPlayer()
    except: 
        if player is not Sipie.cliPlayer:
            Sipie.cliPlayer()

