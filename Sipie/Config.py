#!/usr/bin/python
# -*- coding: utf-8 -*-
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt
#time.time()
# TODO: function for error message checking in __getURL
# TODO: real debug support, not just comments
# TODO: gui setup of config

import os
import sys
import ConfigParser
import getpass
import hashlib

class Section(object):
    def __init__(self, options):
        for (option, value) in options:
            setattr(self, option, value);
 
class Config(object):

    """ SipieConf creates and reads the config file and can return 
      a dictionary for use with the Sipie Class
    """


    def __init__(self):
        """Reads and sets member variables to all config options
        Pass a section to read just that section
        """

        try:
            confdir = os.environ['XDG_CONFIG_HOME']
        except:
            confdir = '%s/.config' % os.environ['HOME']

        self.confpath = os.path.join(confdir, 'sipie')
        self.conffile = os.path.join(self.confpath, 'sipierc')

        # Config Sections
        self.account = None
        self.settings = None
        self.mediaplayer = None

        self.config = ConfigParser.SafeConfigParser()

        self.config.read(self.conffile)

        sections = self.config.sections()
        if len(sections) == 0:
            self.create()

        for section in sections:
            items = self.config.items(section)
            setattr(self, section, Section(items))

    def write(self):
        """ writes the config contents out  """

        fd = open(self.conffile, 'w')
        self.config.write(fd)
        fd.close()
        os.chmod(self.conffile, 448)

    def create(self):
        """ ask questions and create config file."""
        bold = "\033[1m"
        normal = "\033[0;0m"
        print '\n' + bold + 'Welcome to Sipie Setup\n' + normal
        print 'Your username and an encrypted password will be stored in %s/sipierc' % self.confpath
        print 'You can rerun setup anytime by running: sipie --setup' 
        print ''
        if not os.path.isdir(self.confpath):
            os.mkdir(self.confpath)
        self.__makeMeSomeCookies()
        sys.stdout.write('Enter username: ')
        username = sys.stdin.readline().rstrip()
        password = self.cryptPassword(getpass.getpass('Enter password: '))
        print ''
        print 'Please answer the following questions, pressing enter will accept the default values shown in bold text.\n'
        print 'Enter Login Type  (guest or ' + bold + 'subscriber' + normal + ')'
        sys.stdout.write('Login type: ')
        login_type = sys.stdin.readline().rstrip().lower()
        while login_type not in ['subscriber', 'guest']:
            login_type = 'subscriber'
        print '\nAre you using Sirius Cananda  (True or ' + bold + 'False' + normal + ')'
        sys.stdout.write('http://siriuscanada.ca: ')
        canada = sys.stdin.readline().rstrip().lower().capitalize()
        while canada not in ['True', 'False']:
            canada = 'False'
        sys.stdout.write('\nSelect bitrate')
        sys.stdout.write(' (' + bold + 'High' + normal + ' or Low): ')
        bitrate = sys.stdin.readline().rstrip().lower().capitalize()
        while bitrate not in ['High', 'Low']:
            bitrate = 'High'

        for s in ['account', 'settings', 'mediaplayer']:
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
             '-cache 32',
             '-cache-min 4',
             ))

        self.config.set('account', 'username', username)
        self.config.set('account', 'password', password)
        self.config.set('account', 'login_type', login_type)
        self.config.set('account', 'canada', canada)
        self.config.set('settings', 'bitrate', bitrate)
        self.config.set('settings', 'debug', 'False')
        self.config.set('mediaplayer', 'command', '/usr/bin/mplayer')
        self.config.set('mediaplayer', 'options', player_options)
        self.write()

    def cryptPassword(self, password):
        """ used to convert the password to the type sirius wants
         and we don't have to store a plain password on disk """

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

#Static function for reading booleans from config
def toBool(string):
    string = string.lower()
    return string.startswith('t') or string.startswith('y') or string == '1'

