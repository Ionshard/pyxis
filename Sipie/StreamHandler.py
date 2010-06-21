# From http://mak.zopelabs.com/xplay/
# SiriusXPlay by "M. Adam Kendall" 
#
# Modified slighty by Eli Criffield for use in Sipie

import sys, os, time, subprocess
import fcntl
from Config import Config, toBool

#Wrapper Function to Popen function
def pipeopen(cmd, bufsize=0):
    p = subprocess.Popen(cmd, shell=True, bufsize=bufsize,
                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    return (p.stdin, p.stdout)

#
#  Provides simple piped I/O to a process.
#
class StreamHandler(object):
    def __init__(self):

        config = Config()
        self.settings = config.mediaplayer
        self.debug = toBool(config.settings.debug)
        self.location = None
        self.processIn = None
        self.processOut = None
        self.command = "%s %s" % (self.settings.command, self.settings.options)

    def play(self, url):
        mpc = "%s '%s'" % (self.command, url)
        if self.debug:
            print mpc
        (self.processIn, self.processOut) = pipeopen(mpc)
        fcntl.fcntl(self.processOut, fcntl.F_SETFL, os.O_NONBLOCK)

    #
    #  Issues command to process.
    #
    def cmd(self, command):
        if not self.processIn:
            return
        try:
            self.processIn.write(command + "\n")
            self.processIn.flush()  #flush pipe
        except StandardError:
           return

    #
    #  Cleanly closes any IPC resources to process.
    #
    def close(self):

        self.cmd("quit")  #ask process to quit

        try:
            self.processIn.close()   #close pipes
            self.processOut.close()
        except StandardError:
            pass

        self.processIn, self.processOut = None, None

#End of file

