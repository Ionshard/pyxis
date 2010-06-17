# From http://mak.zopelabs.com/xplay/
# SiriusXPlay by "M. Adam Kendall" 
#
# Modified slighty by Eli Criffield for use in Sipie

import sys, os, time, subprocess
if sys.platform == 'win32':
    import win32process, win32api, win32con
else:
    import fcntl


class streamPlayerError(Exception):
    pass

#Wrapper Function to Popen function
def pipeopen(cmd, bufsize=0):
    p = subprocess.Popen(cmd, shell=True, bufsize=bufsize,
                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    return (p.stdin, p.stdout)

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
        from Config import Config
        from Player import Player
        self.__url = None

        if sys.platform == 'win32':
            configdir = '.'
        else:
            configdir = '%s/.sipie'%os.environ['HOME']

        config = Config(configdir)
        sipie = Player(config.items())

        if sys.platform == 'win32':
            mplayerOptions = '-slave -really-quiet -nojoystick -nolirc -user-agent NSPlayer -nomouseinput -prefer-ipv4 -cache '+ sipie.cache + ' -cache-min ' + sipie.cache_min
        else:
            mplayerOptions = '-slave -really-quiet -nojoystick -nolirc -user-agent NSPlayer -nomouseinput -ao pulse,esd,alsa,oss -prefer-ipv4 -cache '+ sipie.cache + ' -cache-min ' + sipie.cache_min
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
            #self.mplayerIn, self.mplayerOut = os.popen4(mpc)  #open pipe
            (self.mplayerIn, self.mplayerOut) = pipeopen(mpc)
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

