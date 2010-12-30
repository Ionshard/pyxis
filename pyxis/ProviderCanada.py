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
from Config import Config, toBool
from Exceptions import AuthError, LoginError, InvalidStream
from Debug import log, logfile
from BeautifulSoup import BeautifulSoup


try:
    from IPython.Shell import IPShellEmbed
    ipshell = IPShellEmbed()
except:
    pass

class ProviderCanada(object):

    def __init__(self, sirius):
        """pass a dictionary of options, like whats returned form 
         SipieConf.items()
      """
        self.sirius = sirius
        config = Config()
        self.account = config.account
        self.settings = config.settings
        self.host = 'mp.siriuscanada.ca'
        self.__headers = {'User-agent': 'Mozilla/5.0 (X11; U; %s i686; en-US; rv:1.8.0.7) github.com/kasuko/pyxis Firefox/1.5.0.7' % \
                                sys.platform}
        self.token = ''
        self.__captchaCallback = None  

    def auth(self):
        """run auth to setup all the cookies you need to get the stream
          self.__captchaCallback should be set to 
          a fuction that accepts a file name as an
          its only argument and returns text found in that image
          (as read by a huMan)

          if no function is passed it will Guess (and fail?)

      """

        url = 'http://%s/sirius/ca/servlet/MediaPlayer' % self.host
        handle = self.sirius.getURL(url)
        data = handle.read()
        handle.close()
        if data.find('bg-now-playing-mac-large') > 0:  #already authed
            return True
        soup = BeautifulSoup(data)
        try:
            self.token = soup.find('input', {'name': 'token'})['value']
        except (NameError, TypeError):
            self.__dbfd('Login-ERROR.html', data)  #DEBUG 0
            print "Login Error token not found:, see Auth-ERROR.html"
            raise LoginError
        try:
            captchaID = soup.find('input', {'name': 'captchaID'})['value']
        except (NameError, TypeError):
            self.__dbfd('Login-ERROR.html', data)  #DEBUG 0
            print "Login Error captchaID not found:, see Auth-ERROR.html"
            raise LoginError
        urlofcaptcha = soup.find('img', {'src': 
                                re.compile('img_\\d{2,4}\\.jpg')})['src']
        capcache = urlofcaptcha.split('/')[-1]
        if os.path.isfile(capcache):
            os.unlink(capcache)
        image = self.sirius.getURL('http://%s%s' % (self.host, urlofcaptcha))
        outfd = open(capcache, 'w')
        outfd.write(image.read())
        outfd.close()
        image.close()
        #print "http://%s%s  %s"%(self.host,urlofcaptcha,capcache) #DEBUG
      #self.printcookies() #DEBUG
      # Get a hUMan to read the captcha to us
        if self.__captchaCallback is None:
            self.__captchaCallback = self.terminalCaptcha
        captcha = self.__captchaCallback(capcache)
        #print "captcha='%s' filename=%s"%(captcha,capcache)#DEBUG
        if os.path.isfile(capcache):
            os.unlink(capcache)

        if self.account.login_type == 'subscriber':
            passwdfield = 'password'
        elif self.account.login_type == 'guest':
            passwdfield = 'encryptedPassword'

        values = {'activity': 'login', 
                  'type': self.account.login_type, 'token': self.token, 
                  'username': self.account.username, 
                  passwdfield: self.account.password, 
                  'captchaID': captchaID, 'captcha_response': captcha, 
                  'loginForm': self.account.login_type}
        url = 'http://%s/sirius/ca/servlet/MediaPlayerLogin/%s' % (self.host, 
                    self.account.login_type)
        fd = self.sirius.getURL(url, values)
        data = fd.read()
        fd.close()
      #self.printcookies() #DEBUG
      #self.__dbfd("login.html",data) #DEBUG
        if data.find('text does not match the image') <> -1:  #IF FOUND
            #self.__dbfd("captcha_mismatch.html",data) #DEBUG
            print ''' ERROR: Captcha Mismatch '''  #DEBUG 0
            raise LoginError
        elif data.find('an error has occurred') <> -1: #IF FOUND
            #self.__dbfd("debug-ERROR.html",data) #DEBUG
            print "Unkown Login Error, see debug-ERROR.html"  #DEBUG 0
            raise LoginError
        elif data.find('Unsuccessful Login') <> -1: #IF FOUND
            #self.__dbfd("debug-ERROR.html",data) #DEBUG
            print "Unsuccessful Login. Please check username and password."  #DEBUG 0
            raise LoginError
        return True

    def tryGetStreams(self):
        """ Returns a list of streams avalible, if it 
         failes with AuthError, try
          Sipie.auth() first, then try again
          Or use getStreams()
      """

        allstreams = []
        url = 'http://%s/sirius/ca/servlet/MediaPlayer' % self.host
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
            print 'LoginError, expired account??, see login-error.html' #DEBUG 0
            raise LoginError
        if data.find('Sorry_Pg3.gif') <> -1:  #IF FOUND
            #DEBUG 0
            print '\nLoginError: to many logins today? see login-error.html'
            logfile('login-error.html', data)  #DEBUG 0
            raise LoginError
        #self.__dbfd("miniplayer.html",data) #DEBUG XXX
      #data = open('small_playing_100.html').read() # DEBUG
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
            print "ERROR getting streams, see streams-DEBUG.html" # DEBUG
            #self.__dbfd('streams-DEBUG.html',data)  # DEBUG
            #return defaultstreams #TESTING
            raise AuthError
        else:
            return allstreams

    def tryGetAsxURL(self, stream):
        """ give this the stream you want to play and this 
         will give you the
         url for the asx, play that url
         if it failes with an AuthError try Sipie.auth() and try again
         or use getAsxUrl
      """

        self.sirius.validateStream()

      # Get hashkey , and the url for the asx
        post = {'activity': 'selectStream', 'stream': stream['channelKey'], 'token': self.token}
        if self.settings.bitrate.lower() == 'high':
            post = {'activity': 'selectBitrate', 'stream': stream['channelKey'], 
                    'bitrate': 'high', 'token': self.token}

        url = 'http://%s/sirius/ca/servlet/MediaPlayer' % self.host
        hd = self.sirius.getURL(url, post)
        data = hd.read()
        data = self.sirius.sanitize(data)
        hd.close()
        if data.find('Sorry_Pg3.gif') > 0:  #IF FOUND
            print "Login Error: to many logins today?"
            print "     see getasxurl-DEBUG.html"
            logfile('getasxurl-DEBUG.html', data)  #DEBUG 0
            raise LoginError
      #self.printcookies() #DEBUG
      #self.__dbfd ("streamselect.html",data) #DEBUG
        soup = BeautifulSoup(data)
        try:
            asxURL = soup.find('param', {'name': 'FileName'})['value']
        except:
            logfile("getasuxurl-ERROR.html",data) #DEBUG
            print "\nAuth Error:, see getasuxurl-ERROR.html\n" #DEBUG
            raise AuthError
        if not asxURL.startswith('http://'):
            asxURL = 'http://%s%s' % (self.host, asxURL)
        return asxURL

    def terminalCaptcha(self,captchaFile):
        print "There is a captcha file, Please open the file %s"%captchaFile
        print "And input the leters below"
        return raw_input(": ")
