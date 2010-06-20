# From http://mak.zopelabs.com/xplay/
# SiriusXPlay by "M. Adam Kendall" 
#
# Modified slighty by Eli Criffield for use in Sipie

import sys, os, time, subprocess
import fcntl

#Wrapper Function to Popen function
def pipeopen(cmd, bufsize=0):
    p = subprocess.Popen(cmd, shell=True, bufsize=bufsize,
                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    return (p.stdin, p.stdout)

#
#  Provides simple piped I/O to an mplayer process.
#
class MplayerHandler(object):
    #
    #  Initializes this mplayerHandler
    #
    def __init__(self, options):
        self.location = None
        self.mplayerIn = None
        self.mplayerOut = None
        self.paused = False
        self.__url = None
        
        mplayerOptions = ' '.join(
            ('-slave',
             '-really-quiet',
             '-nojoystick',
             '-nolirc',
             '-user-agent', 'NSPlayer'
             '-nomouseinput',
             '-prefer-ipv4',
             '-cache 32',
             '-cache-min 4',
             ))
        
        self.command = "%s %s" % (options['mplayer'], mplayerOptions)

    def setURL(self, url):
        self.__url = url

    def play(self):
        if self.__url is None:
            return False
        
        mpc = "%s '%s'" % (self.command, self.__url)
        #print mpc #DEBUG
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

