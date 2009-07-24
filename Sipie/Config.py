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
import md5
import ConfigParser
import getpass

class Config:

    """ SipieConf creates and reads the config file and can return 
      a dictionary for use with the Sipie Class
    """

    def __init__(self, confpath):
        """pass the location of the config directory
           like $HOME/.sipie/ 
           something like $HOME/.sipierc won't work (if thats a file)
           """

        self.execpted = ['username', 'cryptpass', 'login_type', 
                         'bitrate', 'canada']
        self.conffile = os.path.join(confpath,'config')
        #print 
        self.confpath = confpath
        self.config = ConfigParser.SafeConfigParser()
        pass

    def __cryptPassword(self, password):
        """ used to convert the password to the type sirius wants
         and we don't have to store a plain password on disk """

        digest = md5.new()
        digest.update(password)
        secret = digest.hexdigest()
        return secret

    def items(self):
        """ return a dictionary of items from the config
         use this to pass to the Sipie class
      """

        items = {}
        self.config.read(self.conffile)
        try:
            litems = self.config.items('sipie')
        except ConfigParser.NoSectionError:
            self.cliCreate() 
            litems = self.config.items('sipie')
        for (x, y) in litems:
            items[x] = y
	items['configpath'] = self.confpath
        return items

    def write(self):
        """ writes the config contents out  """

        fd = open(self.conffile, 'w')
        self.config.write(fd)
        fd.close()
        os.chmod(self.conffile, 448)

    def set(self, option, value):
        self.config.set('sipie', option, value)

    def cliCreate(self):
        """ if you don't have a config file this will ask the write questions 
      and create one, And it'll return a dictionary of the config like items() 
      would """

        print ''
        print 'username and a crypted password will be stored in %s/config'%self.confpath
        print 'no plain text passwords are stored'
        print 'if you want to change your password remove %s/config'%self.confpath
        print "then run sipie and it'll ask you for username and password again"
        print ''
        if not os.path.isdir(self.confpath):
            os.mkdir(self.confpath)
        sys.stdout.write('Enter username: ')
        username = sys.stdin.readline().rstrip()
        password = getpass.getpass('Enter password: ')
        cryptpass = self.__cryptPassword(password)
        print ''
        print 'Login Type, type guest or subscriber'
        sys.stdout.write('Enter login type: ')
        login_type = sys.stdin.readline().rstrip()
        while login_type not in ['subscriber', 'guest']:
            sys.stdout.write('Invalid: Enter login type: ')
            login_type = sys.stdin.readline().rstrip()
        sys.stdout.write('Are you using Sirius Cananda ')
        sys.stdout.write('(http://siriuscanada.ca)\n True or False: ')
        canada = sys.stdin.readline().rstrip().lower().capitalize()
        while canada not in ['True', 'False']:
            sys.stdout.write('Invalid: Enter True or False for canada: ')
            canada = sys.stdin.readline().rstrip().lower().capitalize()
        try:
            self.config.add_section('sipie')
        except ConfigParser.DuplicateSectionError:
            pass

        self.set('username', username)
        self.set('cryptpass', cryptpass)
        self.set('login_type', login_type)
        self.set('bitrate', 'low')
        self.set('canada', canada)
        self.write()
        return self.items()


