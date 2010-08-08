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

import sys, os, subprocess
import fcntl
import datetime
from Config import Config
from Debug import log, logfile

def pipeopen(cmd, bufsize=0):
    """Wrapper function to subprocess.Popen

    cmd: command to be exectuted

    returns: tuple containing pipes stdin and stdout"""
    p = subprocess.Popen(cmd, shell=True, bufsize=bufsize,
                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    return (p.stdin, p.stdout)

class StreamHandler(object):
    """Handles playing a stream via an external process."""
    def __init__(self, opts):

        config = Config()
        self.settings = config.mediaplayer
        self.location = None
        self.processIn = None
        self.processOut = None
        self.options = opts

        if self.options.record:
            if not os.path.isdir(config.recordings.directory):
                os.makedirs(config.recordings.directory)
            self.settings.options = self.settings.options + ' ' + self.settings.record
            self.settings.options = self.settings.options + config.recordings.directory

        self.command = "%s %s" % (self.settings.command, self.settings.options)

        if os.path.isfile(self.settings.command) == False:
            print "Cannot find media player: " + self.settings.command
            print "Please check your Pyxis media player settings in " + config.conffile
            sys.exit(200)

    def play(self, url, stream):
        """Plays the given url

        url: url to play using external command"""

        if self.options.record:
            stream = stream.replace(' ','') + '_'
            now = datetime.datetime.now()
            filename = stream + now.strftime("%Y-%m-%d_%H-%M-%S") + '.wav'
            mpc = "%s '%s'" % (self.command + filename, url)
        else:
            mpc = "%s '%s'" % (self.command, url)
        log('mpc = %s' % mpc)
        (self.processIn, self.processOut) = pipeopen(mpc)
        fcntl.fcntl(self.processOut, fcntl.F_SETFL, os.O_NONBLOCK)

    def cmd(self, command):
        """Issue a command to the external programs stdin
        
        command: command to be sent to the external program"""
        if not self.processIn:
            return
        try:
            self.processIn.write(command + "\n")
            self.processIn.flush()
        except StandardError:
           return

    def close(self):
        """Cleanly closes any IPC resources to process"""

        self.cmd("quit")

        try:
            self.processIn.close()
            self.processOut.close()
        except StandardError:
            pass

        self.processIn, self.processOut = None, None

