#Pyxis and Original Sipie: Sirius Command Line Player
#Originally From http://mak.zopelabs.com/xplay/
#Copyright (C) Corey Ling, Eli Criffield, M. Adam Kendall
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

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

