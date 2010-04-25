#!/usr/bin/env python
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt

# Very simple example

import Sipie

# Setup a config object to get the user name password 
# canada or not, shit like that

config = Sipie.Config('/home/ecriffield/.sipie/')

# when calling .items() it will try to create the config
# if it doesn't exist
# using an stdin and stdout questions and answers
# If you don't want that make sure that the config file
# already exists with the options SipieConf exepects 

# Sipie.Factory expects a dictionay of config items
# Just like what SipieConf object return with .items()

sipie = Sipie.Factory(config.items())

# setStream will try to authticate with your username and password
# if your not already authed
# and set the current stream to what you give it

sipie.setStream('faction')

# Then you can get the url for the your asx
print sipie.asxURL
print ''


playlist = Sipie.PlaylistPopup(sipie)
playlist.start()

import time
while True:
    time.sleep(30)
    print "Main Loop"
