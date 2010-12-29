#!/usr/bin/python
#Pyxis and Original Sipie: Sirius Command Line Player
#Copyright (C) Corey Ling, Eli Criffield
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

import os
import sys
import ConfigParser
import getpass
import hashlib

class ConfigError(Exception):
    def __init__(self, attr):
        self.attr = attr
    def __str__(self):
        return 'Unable to reference %s from the configuration.\nThis is usually\
 due to a broken config file or a new update.\nPlease run pyxis --setup\
 again to repair the config file.' % self.attr

class Section(object):
    def __init__(self, options):
        for (option, value) in options:
            setattr(self, option, value);

    def __getattr__(self, attr):
        raise ConfigError(attr)

class Config(object):
    """Config is responsible for reading the config file

    It does so by reading sipierc from the users XDG_CONFIG_HOME/sipie
    folder or ~/.config/sipe. It then reads each section to a member variable
    equivalent which then maps all options to more local members.

    Config can be read by accessing config.section.option"""

    def __init__(self):
        """Initializes the Config object

        Takes no parameters and is essentiall read only thus multiple
        copies of Config can be taken as identical."""

        try:
            confdir = os.environ['XDG_CONFIG_HOME']
        except:
            confdir = '%s/.config' % os.environ['HOME']

        self.confpath = os.path.join(confdir, 'pyxis')
        self.conffile = os.path.join(self.confpath, 'pyxisrc')

        # Config Sections
        self.account = None
        self.settings = None
        self.mediaplayer = None

        self.config = ConfigParser.SafeConfigParser()
        self.config.read(self.conffile)

        sections = self.config.sections()
        for section in sections:
            items = self.config.items(section)
            setattr(self, section, Section(items))

        if not self.validate():
            self.create()

    def validate(self):
        """Validate that the current config file works with this version.
        Returns True if the config is valid, else False.
        """
        return (self.account and self.settings and self.mediaplayer)

    def write(self):
        """Writes the contents of the ConfigParser to the config file"""

        fd = open(self.conffile, 'w')
        self.config.write(fd)
        fd.close()
        os.chmod(self.conffile, 448)

    def create(self):
        """Gather required information from user and create config file"""
        bold = "\033[1m"
        normal = "\033[0;0m"
        print '\n' + bold + 'Welcome to Pyxis Setup\n' + normal
        print 'Your username and an encrypted password will be stored in %s' % self.conffile
        print 'You can rerun setup anytime by running: pyxis --setup' 
        print ''
        if not os.path.isdir(self.confpath):
            os.makedirs(self.confpath)
        self.__makeMeSomeCookies()
        sys.stdout.write('Enter username: ')
        username = sys.stdin.readline().rstrip()
        password = self.cryptPassword(getpass.getpass('Enter password: '))
        print ''
        print 'Please answer the following questions, pressing enter will accept the default values shown in bold text.\n'
        print 'Enter Login Type (guest or ' + bold + 'subscriber' + normal + ')'
        sys.stdout.write('Login type: ')
        login_type = sys.stdin.readline().rstrip().lower()
        while login_type not in ['subscriber', 'guest']:
            login_type = 'subscriber'
        print '\nAre you using Sirius Cananda (True or ' + bold + 'False' + normal + ')'
        sys.stdout.write('http://siriuscanada.ca: ')
        canada = sys.stdin.readline().rstrip().lower().capitalize()
        while canada not in ['True', 'False']:
            canada = 'False'
        sys.stdout.write('\nSelect bitrate')
        sys.stdout.write(' (' + bold + 'High' + normal + ' or Low): ')
        bitrate = sys.stdin.readline().rstrip().lower().capitalize()
        while bitrate not in ['High', 'Low']:
            bitrate = 'High'

        for s in ['account', 'settings', 'mediaplayer', 'debug', 'recordings']:
            try:
                self.config.add_section(s)
            except ConfigParser.DuplicateSectionError:
                pass

        player_options = ' '.join(
            ('-slave',
             '-really-quiet',
             '-nojoystick',
             '-nolirc',
             '-user-agent', 'NSPlayer'
             '-nomouseinput',
             '-prefer-ipv4',
             '-cache', '32',
             '-cache-min', '4',
             ))

        self.config.set('account', 'username', username)
        self.config.set('account', 'password', password)
        self.config.set('account', 'login_type', login_type)
        self.config.set('account', 'canada', canada)
        self.config.set('settings', 'bitrate', bitrate)
        self.config.set('mediaplayer', 'command', '/usr/bin/mplayer')
        self.config.set('mediaplayer', 'options', player_options)
        self.config.set('mediaplayer', 'record', '-ao pcm:file=')
        self.config.set('recordings', 'directory', os.environ['HOME'] + '/pyxis/')
        self.config.set('debug', 'debug', 'False')
        self.config.set('debug', 'directory', '~/pyxisdebug')
        try:
            import pynotify
        except:
            self.config.set('settings', 'notifications', 'No')
        else:
            self.config.set('settings', 'notifications', 'Yes')

        self.write()

    def cryptPassword(self, password):
        """Convert the plaintext password to its md5 equivalent

        This allows us to not have to store plaintext passwords in the config
        file as Sirius only requires the md5 of the password for authentication
        """

        password = password.encode("utf-8")
        digest = hashlib.md5()
        digest.update(password)
        secret = digest.hexdigest()
        return secret


    def __makeMeSomeCookies(self):
        cookiepuss = """    # Netscape HTTP Cookie File
    # http://www.netscape.com/newsref/std/cookie_spec.html
    # This is a generated file!  Do not edit.

www.sirius.com	FALSE	/	FALSE		sirius_consumer_type	sirius_online_subscriber
www.sirius.com	FALSE	/	FALSE		sirius_login_type	subscriber
"""
        fd = open(os.path.join(self.confpath,'cookies.txt'), 'w')
        fd.write(cookiepuss)
        fd.close()

def toBool(string):
    """Function that converts a string representation of a bool to a bool

    This can read 0/1 yes/no or true/false
    """
    string = string.lower()
    return string.startswith('t') or string.startswith('y') or string == '1'

