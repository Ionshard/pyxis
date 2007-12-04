#!/usr/bin/python
# -*- coding: utf-8 -*-
# Josh Zeno <TwoOneSix@thatclothingco.com>
# mythPlayer.py: This is a sipie player that it tweaked specifically for MythTV usage
#		and is designed to be run as a background process that is managed by the script
#		sipie_myth (found at: http://www.mythtv.org/wiki/index.php/Integrate_Sirius)
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt
####################################
# What makes this player different?
# --You must send the stream name as an argument: i.e. mythSipie octane
# --Is able to run as a "friendly" background process using sipie_myth as mentioned above
# --Gives the user the option to disable pynotify popups and set the popup timeout
# --Adds the sipie icon to the pynotify pop-up window
# --Does not keep your Sirius session open so you have to be careful how often you change streams

def mythPlayer():
    from Sipie.Config import Config
    from Sipie.Player import Player
    from Sipie import StreamHandler
    import sys 
    import os 
    import time

    global sipie

    tryPopups = True # Set as False to disable pop-ups
    notifySeconds = 120000 # This is a MAX time (in ms) to show a single song name. Default: 120000 (2 min)

    if tryPopups:
        try:
            import pynotify
            from pkg_resources import Requirement, resource_filename
            pynotify.init("mythSipie")
        except:
            print "WARN: Not found! Is pynotify installed?"
            tryPopups = False

    def getIcon():
        icon_file = resource_filename(Requirement.parse("Sipie"),"Sipie/data/sipie.png")
        if os.path.isfile(icon_file):
            return icon_file

    configdir = '%s/.sipie'%os.environ['HOME']
    streamHandler = StreamHandler.mplayerHandler('/usr/bin/mplayer') # haven't tried other handlers yet
    config = Config(configdir)
    sipie = Player(config.items())
    sipie.setPlayer(streamHandler)

    FirstLoop = True
    while True:
        if len(sys.argv) == 2 and FirstLoop:
            stream = sys.argv[1].lower()
        elif sys.argv[0].lower().find("sipie") == -1 and FirstLoop:
            stream = os.path.basename(sys.argv[0])

        try:
            sipie.setStream(stream)
        except :
            FirstLoop = False
            print "******FATAL: Invalid Stream!******"
            sipie.close()
            sys.exit()

        sipie.play()

	# We have to handle pynotify differently from the command line to keep it from crashing the player
        while True:
            playing = sipie.nowPlaying()
            if playing['new']:
                if tryPopups:
                    nPop = pynotify.Notification(playing['stream'], playing['playing'], getIcon())
                    nPop.set_timeout(notifySeconds)
                    nPop.show()
                print playing['logfmt']

            try:
                time.sleep(30)
            except KeyboardInterrupt:
		print "Thanks for playing!"
                sipie.close()
		sys.exit()
            FirstLoop = False



if __name__ == '__main__':
    mythPlayer()
