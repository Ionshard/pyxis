# From http://mak.zopelabs.com/xplay/
# SiriusXPlay by "M. Adam Kendall" 
#
# Modified slighty by Eli Criffield for use in Sipie

import sys, os, time
if sys.platform == 'win32':
    import win32process, win32api, win32con
else:
    import fcntl


class streamPlayerError(Exception):
    pass

#
#  Provides simple piped I/O to an mplayer process.
#
class mplayerHandler:

    location, mplayerIn, mplayerOut = None, None, None
    paused = False

    #
    #  Initializes this mplayerHandler
    #
    def __init__(self, location):
        self.__url = None
        #mplayerOptions = '-slave -really-quiet -nojoystick -nolirc -user-agent NSPlayer -nomouseinput -ao esd,alsa,oss -prefer-ipv4 -cache 32 -playlist '
        mplayerOptions = '-slave -really-quiet -nojoystick -nolirc -user-agent NSPlayer -nomouseinput -ao esd,alsa,oss -prefer-ipv4 -cache 32 '
        if sys.platform == 'win32':
            #mplayerOptions = '-slave -really-quiet -nojoystick -nolirc -user-agent NSPlayer -nomouseinput -prefer-ipv4 -cache 32 -playlist '
            mplayerOptions = '-slave -really-quiet -nojoystick -nolirc -user-agent NSPlayer -nomouseinput -prefer-ipv4 -cache 32 '
        self.command = "%s %s "%(location,mplayerOptions)

    def setURL(self, url):
        self.__url = url

    def play(self):
        if self.__url is None:
            return False
        mpc = "%s '%s'"%(self.command,self.__url)
        #print mpc #DEBUG
        if sys.platform == 'win32':
            si = win32process.STARTUPINFO()
            si.dwFlags = win32process.STARTF_USESTDHANDLES
            si.hStdInput = win32api.GetStdHandle(win32api.STD_INPUT_HANDLE)
            si.hStdOutput = win32api.GetStdHandle(win32api.STD_OUTPUT_HANDLE)
            si.hStdError = win32api.GetStdHandle(win32api.STD_ERROR_HANDLE)
            info = win32process.CreateProcess(
                None,
                mpc,
                None,
                None,
                1,
                win32process.DETACHED_PROCESS,
                None,
                None,
                si)
            self.handle = info[0]
        else:
            self.mplayerIn, self.mplayerOut = os.popen4(mpc)  #open pipe
            fcntl.fcntl(self.mplayerOut, fcntl.F_SETFL, os.O_NONBLOCK)

    #   Plays the specified filename
    def playX(self, filename):
        if not self.mplayerIn:
            return
        cmd = "loadlist %s" % filename
        self.cmd(cmd)

    # mutes
    def mute(self):
        if not self.mplayerIn:
            return
        self.cmd('mute')

    #
    #  Issues command to mplayer.
    #
    def cmd(self, command):
        if not self.mplayerIn:
            return
        try:
            self.mplayerIn.write(command + "\n")
            self.mplayerIn.flush()  #flush pipe
        except StandardError:
           return

    #
    #  Toggles pausing of the current mplayer job and status query.
    #
    def pause(self):
        if not self.mplayerIn:
            return

        if self.paused:  #unpause
            self.paused = False

        else:  #pause
            self.paused = True

        self.cmd("pause")

    #
    #  Cleanly closes any IPC resources to mplayer.
    #
    def close(self):

        if sys.platform == 'win32':
            win32process.TerminateProcess(self.handle, 0)
        else:
            if self.paused:  #untoggle pause to cleanly quit
                self.pause()

            self.cmd("quit")  #ask mplayer to quit

            try:
                self.mplayerIn.close()   #close pipes
                self.mplayerOut.close()
            except StandardError:
                pass

        self.mplayerIn, self.mplayerOut = None, None

#End of file


#
#  Provides simple piped I/O to an vlc process.
#
class vlcHandler:

    location, vlcIn, vlcOut = None, None, None
    paused = False
    muted = False

    #
    #  Initializes this vlcHandler
    #
    def __init__(self, location):
        self.location = location
        self.__url = None

    def setURL(self, url):
        self.__url = url

    def play(self):
        if self.__url is None:
            return False
        if sys.platform == 'win32':
            cli = "%s %s" % (self.location, self.__url)
            si = win32process.STARTUPINFO()
            si.dwFlags = win32process.STARTF_USESTDHANDLES
            si.hStdInput = win32api.GetStdHandle(win32api.STD_INPUT_HANDLE)
            si.hStdOutput = win32api.GetStdHandle(win32api.STD_OUTPUT_HANDLE)
            si.hStdError = win32api.GetStdHandle(win32api.STD_ERROR_HANDLE)
            info = win32process.CreateProcess(
                None,
                cli,
                None,
                None,
                1,
                win32con.CREATE_NO_WINDOW,
                None,
                None,
                si)
            self.handle = info[0]
        else:
            cli = self.location + " --intf rc --rc-fake-tty --novideo --quiet"
            self.vlcIn, self.vlcOut = os.popen4(cli)
            fcntl.fcntl(self.vlcOut, fcntl.F_SETFL, os.O_NONBLOCK)
            time.sleep(10)

            try:
            	self.cmd('add %s' % self.__url)
                if sys.platform != 'darwin':
		   self.vlcOut.readlines(5)
                else:
                   self.vlcOut.readlines(4)
            except:
                raise streamPlayerError
            self.cmd('volume')  
            currVolume = int(self.vlcOut.readline().split(' ')[2])
            self.volume = 255
    
    #   Plays the specified filename
    def playX(self):
        if not self.vlcIn:
            return
        self.cmd('play')
    
    # mutes
    def mute(self):
        if not self.muted:
            self.cmd('volume 0')
            self.muted = True
        else:
            self.cmd('volume %s' % self.volume)
            self.muted = False
            
        
    #
    #  Issues command to vlc.
    #
    def cmd(self, command):
        if not self.vlcIn:
            return
        try:
            self.vlcIn.write(command + "\n")
            self.vlcIn.flush()  #flush pipe
        except StandardError:
            raise streamPlayerError
            
    #
    #  Toggles pausing of the current vlc job and status query.
    #
    def pause(self):
        if not self.vlcIn:
            return
            
        if self.paused:  #unpause   
            self.paused = False
            
        else:  #pause
            self.paused = True
            
        self.cmd("pause")
    
    #
    #  Cleanly closes any IPC resources to vlc.
    #
    def close(self):
        if sys.platform == 'win32':
            try:
                win32process.TerminateProcess(self.handle, 0)
            except:
                pass
        else:
            if self.paused:  #untoggle pause to cleanly quit
                self.pause()
            
            self.cmd("quit")  #ask vlc to quit
            
            try:            
                self.vlcIn.close()   #close pipes
                self.vlcOut.close()
            except StandardError:
                pass
        
        self.vlcIn, self.vlcOut = None, None        
 
#End of file


#
#  Provides simple piped I/O to an Window Media Player
#
class wmpHandler:

    WM_COMMAND = 0x111
    paused = False

    #
    #  Initializes this mplayerHandler
    #

    def __init__(self, location):
        self.location = location
        self.__url = None
        self.handle = 0

    def setURL(self, url):
        self.__url = url

    def play(self):
        if self.__url is None:
            return False
        mpc = self.location + " " + self.__url 
        if sys.platform == 'win32':
            si = win32process.STARTUPINFO()
            si.dwX=0
            si.dwY=0
            si.dwXSize=640
            si.dwYSize=480
            si.dwFlags = win32process.STARTF_USESTDHANDLES
            si.hStdInput = win32api.GetStdHandle(win32api.STD_INPUT_HANDLE)
            si.hStdOutput = win32api.GetStdHandle(win32api.STD_OUTPUT_HANDLE)
            si.hStdError = win32api.GetStdHandle(win32api.STD_ERROR_HANDLE)
            info = win32process.CreateProcess(
                None,
                mpc,
                None,
                None,
                1,
                win32process.DETACHED_PROCESS,
                None,
                None,
                si)
            self.handle = info[0]

        else:
            # mac support
            pass
    
    # mutes
    def mute(self):
        if sys.platform == 'win32':
            winHandle = win32gui.FindWindow('wmplayerApp', None)
            wParam = 0x00004981
            lParam = 0x00000000
            win32api.SendMessage(winHandle, self.WM_COMMAND, wParam, lParam )
        else:
            pass
            # mac support

    #  Toggles pausing
    #
    def pause(self):
        if self.paused:  #unpause   
            self.paused = False
            
        else:  #pause
            self.paused = True
            
        if sys.platform == 'win32':
            winHandle = win32gui.FindWindow('wmplayerApp', None)
            wParam = 0x00004978
            lParam = 0x00000000
            win32api.SendMessage(winHandle, self.WM_COMMAND, wParam, lParam ) 
        else:
            pass
            # mac support
    #
    #  Cleanly closes 
    #
    def close(self):
        
        if sys.platform == 'win32':
            win32process.TerminateProcess(self.handle, 0)
            time.sleep(1)
        else:
            if self.paused:  #untoggle pause to cleanly quit
                self.pause()
            
#End of file


#
#  Provides simple piped I/O to an WinAmp process.
#
class winampHandler:

    windowName = "winampSirius"
    WM_COMMAND = 0x111
    WM_USER = 0x400
    lParam = 0x00000000
    paused = False
    muted = False

    #
    #  Initializes this winampHandler
    #
    def __init__(self, location):
        self.location = location
        self.__url = None

    def setURL(self, url):
        self.__url = url

    def play(self):
        if self.__url is None:
            return False
        mpc = self.location + " /CLASS=\"" + self.windowName + "\" " + __url
        if sys.platform == 'win32':
            si = win32process.STARTUPINFO()
            si.dwFlags = win32process.STARTF_USESTDHANDLES
            si.hStdInput = win32api.GetStdHandle(win32api.STD_INPUT_HANDLE)
            si.hStdOutput = win32api.GetStdHandle(win32api.STD_OUTPUT_HANDLE)
            si.hStdError = win32api.GetStdHandle(win32api.STD_ERROR_HANDLE)
            info = win32process.CreateProcess(
                None,
                mpc,
                None,
                None,
                1,
                win32process.DETACHED_PROCESS,
                None,
                None,
                si)
            self.handle = info[0]
            time.sleep(3)
            winHandle = win32gui.FindWindow(self.windowName, None)
			# Hide main window
            #wParam = 0x00009d42 
            #win32api.SendMessage(winHandle, self.WM_COMMAND, wParam, self.lParam )
			# Hide playlist window
            wParam = 0x00009c68 
            win32api.SendMessage(winHandle, self.WM_COMMAND, wParam, self.lParam )
			# Set a known volume level
            wParam = 0xc8
            win32api.SendMessage(winHandle, self.WM_USER, wParam, 0x7a )
        else:
            # mac support
            pass
    
    # mutes
    def mute(self):
        if sys.platform == 'win32':
            winHandle = win32gui.FindWindow(self.windowName, None)
            if self.muted:
                self.muted = False
                wParam = 0xc8
                win32api.SendMessage(winHandle, self.WM_USER, wParam, 0x7a )
            else:
                self.muted = True
                wParam = 0x0
                win32api.SendMessage(winHandle, self.WM_USER, wParam, 0x7a )
        else:
            pass
            # mac support

    #  Toggles pausing
    #
    def pause(self):
        if self.paused:  #unpause   
            self.paused = False
            
        else:  #pause
            self.paused = True
            
        if sys.platform == 'win32':
            winHandle = win32gui.FindWindow(self.windowName, None)
            wParam = 0x00004978
            win32api.SendMessage(winHandle, self.WM_COMMAND, wParam, self.lParam ) 
        else:
            pass
            # mac support
    #
    #  Cleanly closes 
    #
    def close(self):
        
        if sys.platform == 'win32':
            win32process.TerminateProcess(self.handle, 0)
        else:
            if self.paused:  #untoggle pause to cleanly quit
                self.pause()
            
#End of file


#
#  Provides simple piped I/O to an xine process.
#
class xineHandler:

    location, xineIn, xineOut = None, None, None
    paused = False
    muted = False

    #
    #  Initializes this xineHandler
    #
    def __init__(self, location):
        self.location = location
        self.__url = None

    def setURL(self, url):
        self.__url = url

    def play(self):
         if self.__url is None:
            return False
         if sys.platform == 'win32':
            cli = "%s %s" % (location, __url)
            si = win32process.STARTUPINFO()
            si.dwFlags = win32process.STARTF_USESTDHANDLES
            si.hStdInput = win32api.GetStdHandle(win32api.STD_INPUT_HANDLE)
            si.hStdOutput = win32api.GetStdHandle(win32api.STD_OUTPUT_HANDLE)
            si.hStdError = win32api.GetStdHandle(win32api.STD_ERROR_HANDLE)
            info = win32process.CreateProcess(
                None,
                cli,
                None,
                None,
                1,
                win32con.CREATE_NO_WINDOW,
                None,
                None,
                si)
            self.handle = info[0]
         else:
            cli = self.location + " --no-gui --no-splash --stdctl --session mrl=%s" % self.__url
            #cli = self.location + " --no-gui --no-splash --stdctl --bug-report=/home/akendall/bartender.mp3"
            #print cli # DEBUG
            self.xineIn, self.xineOut = os.popen4(cli)
            fcntl.fcntl(self.xineOut, fcntl.F_SETFL, os.O_NONBLOCK)

            time.sleep(2)
            try:
                print self.xineOut.readlines(1)
            except:
                raise streamPlayerError
    
    #   Plays the specified filename
    def play(self):
        if not self.xineIn:
            return
        self.cmd('play')
    
    # mutes
    def mute(self):
        if not self.muted:
            self.cmd('mute')
            self.muted = True
        else:
            self.cmd('mute')
            self.muted = False
            
        
    #
    #  Issues command to xine.
    #
    def cmd(self, command):
        if not self.xineIn:
            return
        try:
            self.xineIn.write(command + "\n")
            self.xineIn.flush()  #flush pipe
        except StandardError:
            raise streamPlayerError
            
    #
    #  Toggles pausing of the current xine job and status query.
    #
    def pause(self):
        if not self.xineIn:
            return
            
        if self.paused:  #unpause   
            self.paused = False
            
        else:  #pause
            self.paused = True
            
        self.cmd("pause")
    
    #
    #  Cleanly closes any IPC resources to xine.
    #
    def close(self):
        if sys.platform == 'win32':
            try:
                win32process.TerminateProcess(self.handle, 0)
            except:
                pass
        else:
            if self.paused:  #untoggle pause to cleanly quit
                self.pause()
            
            self.cmd("quit")  #ask xine to quit
            
            try:            
                self.xineIn.close()   #close pipes
                self.xineOut.close()
            except StandardError:
                pass
        
        self.xineIn, self.xineOut = None, None        

# Gstreamer ( gnome ) handler
class gstHandler:
    def __init__(self):
        import gst 
        self.gst = gst
        self.playing = False
        self.player = self.gst.element_factory_make("playbin", "player")
        self.on_eos = False
        self.muted = False

        bus = self.player.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        bus.connect('sync-message::element', self.onSyncMessage)
        bus.connect('message', self.onMessage)

    def onSyncMessage(self, bus, message):
        if message.structure is None:
            return
        if message.structure.get_name() == 'prepare-xwindow-id':
            message.src.set_property('force-aspect-ratio', True)
            
    def onMessage(self, bus, message):
        t = message.type
        if t == self.gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            if self.on_eos:
                self.on_eos()
            self.playing = False
        elif t == self.gst.MESSAGE_EOS:
            if self.on_eos:
                self.on_eos()
            self.playing = False

    def setURL(self, location):
        self.player.set_property('uri', location)

    def queryPosition(self):
        "Returns a (position, duration) tuple"
        try:
            position, format = self.player.query_position(self.gst.FORMAT_TIME)
        except:
            position = self.gst.CLOCK_TIME_NONE

        try:
            duration, format = self.player.query_duration(self.gst.FORMAT_TIME)
        except:
            duration = self.gst.CLOCK_TIME_NONE

        return (position, duration)

    def seek(self, location):
        """
        @param location: time to seek to, in nanoseconds
        """
        self.gst.debug("seeking to %r" % location)
        event = self.gst.event_new_seek(1.0, self.gst.FORMAT_TIME,
            self.gst.SEEK_FLAG_FLUSH | self.gst.SEEK_FLAG_ACCURATE,
            self.gst.SEEK_TYPE_SET, location,
            self.gst.SEEK_TYPE_NONE, 0)

        res = self.player.send_event(event)
        if res:
            self.gst.info("setting new stream time to 0")
            self.player.set_new_stream_time(0L)
        else:
            self.gst.error("seek to %r failed" % location)

    def pause(self):
        self.gst.info("pausing player")
        self.player.set_state(self.gst.STATE_PAUSED)
        self.playing = False

    def play(self):
        self.gst.info("playing player")
        self.player.set_state(self.gst.STATE_PLAYING)
        self.playing = True

    def mute(self):
        if not self.muted:
           self.stop()
           self.muted = True
        else:
           self.play()
           self.muted = False
        
    def stop(self):
        self.player.set_state(self.gst.STATE_NULL)
        self.gst.info("stopped player")

    def close(self):
        self.player.set_state(self.gst.STATE_NULL)
        self.gst.info("closing player")

    def getState(self, timeout=1):
        return self.player.get_state(timeout=timeout)

    def is_playing(self):
        return self.playing
 
#End of file
