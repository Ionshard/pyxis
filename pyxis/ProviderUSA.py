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

import cookielib
import urllib2
import urllib
import os
import sys
import re
import time
from Debug import log, logfile
from Config import Config, toBool
from Exceptions import AuthError, LoginError, InvalidStream
from BeautifulSoup import BeautifulSoup

class ProviderUSA(object):
    """Handles all access to the SIRIUS USA website"""
    def __init__(self, sirius):
	self.sirius = sirius
        #Get settings
        config = Config()
        self.account = config.account
        self.settings = config.settings

        self.host = 'www.sirius.com'
        self.__headers = {'User-agent': 'Mozilla/5.0 (X11; U; %s i686; en-US; rv:1.8.0.7) github.com/kasuko/pyxis Firefox/1.5.0.7' % \
                        sys.platform}
        self.token = ''

    def auth(self):
        """run auth to setup all the cookies you need to get the stream
          self.__captchaCallback should be set to 
          a fuction that accepts a file name as an
          its only argument and returns text found in that image
          (as read by a huMan)

          if no function is passed it will Guess (and fail?)

        """
        log('Authenticating ...')
        #Am i authed, should be its own function really
        data = self.sirius.getURL(
          'http://www.sirius.com/player/listen/play.action').read()
        if 'NOW PLAYING TITLE:START' in data:
          log('Authenticated')
          return True

        session = self.sirius.findSessionID()
	log('SESSIONID= %s' % session)
        if not session:
          getURL(
            'http://www.sirius.com/player/home/siriushome.action').read()
          session = self.sirius.findSessionID()
        if not session:
          raise LoginError

        authurl = 'http://www.sirius.com/player/login/siriuslogin.action;jsessionid=%s' % session

        postdict = { 'userName': self.account.username,
                     '__checkbox_remember': 'true',
                     'password': self.account.password,
                     'captchaEnabled': 'true',
                     'timeNow': 'null',
                     'captcha_response': 'rc3k',
                   }

        post = urllib.urlencode(postdict) + '&captchaID=%3E%3A0%08g%60n'
        data = self.sirius.getURL(authurl, poststring=post).read()
        if '<title>SIRIUS Player' in data:
          log("got valid page at: " + authurl + "\n")
          return True
        else:
          raise LoginError

    def tryGetStreams(self):
        """ Returns a list of streams avalible, if it 
         failes with AuthError, try
          Sirius.auth() first, then try again
          Or use getStreams()
      """
        log('Getting streams ...')
        allstreams = []
        url = 'http://www.sirius.com/player/listen/play.action?resizeActivity=minimize'
        hd = self.sirius.getURL(url)
        data = hd.read()
        hd.close()
        if data.find('name="selectedStream"') == -1:  #IF NOT FOUND
            post = {'activity': 'minimize', 'token': self.token}
            hd = self.sirius.getURL(url, post)
            data = hd.read()
            hd.close()
        if data.find('unable to log you in') <> -1:  #IF FOUND
            logfile('login-error.html', data)  #DEBUG 0
            print 'LoginError, expired account?' #DEBUG 0
            raise LoginError
        if data.find('Sorry_Pg3.gif') <> -1:  #IF FOUND
            print '\nLoginError: to many logins today?'
            logfile('login-error.html', data)  #DEBUG 0
            raise LoginError
        data = self.sirius.sanitize(data)
        soup = BeautifulSoup(data)
        for catstrm in soup.findAll('option'):
            if catstrm['value'].find('|') <> -1:  # IF FOUND
                chunks = catstrm['value'].split('|')
                stream = {
                    'channelKey': chunks[2],
                    'genreKey':  chunks[1],
                    'categoryKey': chunks[0],
                    'selectedStream': catstrm['value'],
                    'longName': catstrm.contents[0].split(';')[-1].lower()
                    }
                allstreams.append(stream)
        if len(allstreams) < 5:
            log("ERROR getting streams, see streams-DEBUG.html") # DEBUG
            logfile('streams-DEBUG.html',data)  # DEBUG
            raise AuthError
        else:
	    logfile('streams.log', repr(allstreams))
            log('Streams retrieved, see streams.log')
            return allstreams

    def tryGetAsxURL(self, stream):
        """ give this the stream you want to play and this 
         will give you the
         url for the asx, play that url
         if it failes with an AuthError try Sirius.auth() and try again
         or use getAsxUrl
      """

        self.sirius.validateStream()

        postdict = { 'channelKey': stream['channelKey'],
                     'genreKey': stream['genreKey'],
                     'categoryKey': stream['categoryKey'],
                     'selectedStream': stream['selectedStream'],
                     'stopped': 'no',
                   }
        data = self.sirius.getURL(
            'http://www.sirius.com/player/listen/play.action',
            postdict).read()

        data = self.sirius.sanitize(data)
        soup = BeautifulSoup(data)
        try:
            firstURL = soup.find('param', {'name': 'FileName'})['value']
        except TypeError:
             logfile("getasuxurl-ERROR.html",data) #DEBUG
             log("\nAuth Error:, see getasuxurl-ERROR.html\n") #DEBUG
             raise AuthError
        if not firstURL.startswith('http://'):
            firstURL = 'http://%s%s' % (self.host, firstURL)
        asxURL = self.sirius.getURL(firstURL).read()
        log('asxURL = %s' % asxURL)
        return asxURL
