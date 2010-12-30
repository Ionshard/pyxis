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
from ProviderUSA import ProviderUSA
from ProviderCanada import ProviderCanada
from Exceptions import AuthError, LoginError, InvalidStream
from Debug import log, logfile
from xml.dom.minidom import parse
import htmlfixes

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    print 'Missing dependency: BeautifulSoup'
    print ' to install run `easy_install BeautifulSoup`'
    print ' or if you have apt try '
    print ' apt-get install python-beautifulsoup'
    print ''
    print 'or download the beautifulsoup.py module and put it in the current directory.'
    print 'http://www.crummy.com/software/BeautifulSoup/'
    sys.exit(300)

if 'find' not in dir(BeautifulSoup):
    print 'Pyxis requires a newer version of Beautiful soup:'
    print 'Get the latest version from: http://www.crummy.com/software/BeautifulSoup/'
    sys.exit(301)

class Sirius(object):
    """Handles all access to the SIRIUS website"""
    def __init__(self):
        #Get settings
        config = Config()
        self.account = config.account
        self.settings = config.settings

        self.host = 'www.sirius.com'
        self.__headers = {'User-agent': 'Mozilla/5.0 (X11; U; %s i686; en-US; rv:1.8.0.7) github.com/kasuko/pyxis Firefox/1.5.0.7' % \
                        sys.platform}
        self.token = ''
        self.__stream = None
        self.asxURL = None
        self.allstreams = []
        self.playing = None
        self.__cookie_jar = None

        if self.account.login_type not in ['subscriber', 'guest']:
            print 'invalid login_type in config file'
            sys.exit(101)

        if toBool(self.account.canada):
            self.provider = ProviderCanada(self)
        else:
            self.provider = ProviderUSA(self)

        self.cookiefile = os.path.join(config.confpath, 'cookies.txt')
        self.playlist = os.path.join(config.confpath, 'playlist')
        self.__setupOpener()

    def __setupOpener(self):
        """Initialize proper cookies and parameters for website retrival"""
        self.__cookie_jar = cookielib.MozillaCookieJar(self.cookiefile)
        cookie_handler = urllib2.HTTPCookieProcessor(self.__cookie_jar)
        if os.path.isfile(self.cookiefile):
            self.__cookie_jar.load()
         # this way its all one big session, even on exit and restart
            self.__cookie_jar.load(ignore_discard=True, ignore_expires=
                                 True)

        http_proxy = os.environ.get('http_proxy')
        if http_proxy is not None:
            proxy_handler = urllib2.ProxyHandler({'http': http_proxy})
            opener = urllib2.build_opener(cookie_handler, proxy_handler)
        else:
            opener = urllib2.build_opener(cookie_handler)
        urllib2.install_opener(opener)

    def sanitize(self, data):
        """ Sanitizes Data against specific errors in the Sirus HTML that
        Beautiful soup can not handle.
        """
        for sub in htmlfixes.subs:
            data = re.sub(sub[0], sub[1], data)
 
        logfile('sanitize.html', data) #DEBUG

        return data

    def findSessionID(self):
        """ finds the session ID cookie and returns the value """
        for (index, cookie) in enumerate(self.__cookie_jar):
          if 'JSESSIONID' in cookie.name:
            return cookie.value
        return False

    def getURL(self, url, postdict=None, poststring=None):
        """ get a url, the second arg could be dictionary of 
         options for a post 
         If there is no second option use get
         This will use the cookies and tokens for this instance 
         of Sirius
         returns a file handle
      """

        if postdict:
            postdata = urllib.urlencode(postdict)
        else:
            postdata = None
        if poststring:
            postdata = poststring

        log("POST=%s" % postdata)#DEBUG
        log("url=%s" % url) #DEBUG

        req = urllib2.Request(url, postdata, self.__headers)
        handle = None
        while handle is None:
            try:
                handle = urllib2.urlopen(req)
            except urllib2.URLError:
                print("Error while fetching %s\nTrying again in 30 seconds..." % url);
                time.sleep(30);
                handle = None
        self.__cookie_jar.save(ignore_discard=True, ignore_expires=True)
        return handle

    def getAsxURL(self):
        ''' Returns an the url of the asx for the self.__stream,
        Diffrent from tryGetAsxURL it will try to authticate insted of
        fail if its needs to
        '''
        try:
            url = self.provider.tryGetAsxURL(self.__stream)
        except AuthError:
            self.provider.auth()
            url = self.provider.tryGetAsxURL(self.__stream)
        return url

    def getStreams(self):
        ''' Returns an the list of streams
        Diffrent from tryGeStreams it will try to authticate insted of
        fail if its needs to
        '''
        try:
            streams = self.provider.tryGetStreams()
        except AuthError:
            self.provider.auth()
            streams = self.provider.tryGetStreams()
        return streams

    def validateStream(self, stream=None):
        '''checks if stream is valid if theres no agument then it checks 
        self.__stream'''
        if stream is None: 
            stream = self.__stream

	log('Validationg stream %s' % stream)
        if len(self.allstreams) < 5:
            self.allstreams = self.getStreams()
        if stream not in self.allstreams:
            log('stream %s invalid' % stream)
            raise InvalidStream

    def setStreamByLongName(self, longName):
        '''Sets the currently playing stream to the stream refered to by
        longname'''

	log('Set Stream to %s' % longName)
        #print 'setStreamByLongName:',longName #DEBUG
        if len(self.allstreams) < 5:
            self.allstreams = self.getStreams()
            
        for stream in self.allstreams:
          if stream['longName'].lower() == longName.lower():
            #print 'setStreamByLongName, stream:',stream #DEBUG
            self.__stream = stream
            log('Stream set to %s' % stream)
            return
        raise InvalidStream

    def getNowPlaying(self):
        '''return a dictionary for current song/artist per channel'''
        nowplaying = {}
        url = 'http://www.siriusxm.com/padData/pad_provider.jsp?all_channels=y'
        try:
            sirius_xml = parse(urllib.urlopen(url))
        except Exception:
            log("ERROR getting now-playing list: %s" % url)
            return "FAILURE"

        for channels in sirius_xml.getElementsByTagName('event'):
            channel = channels.getElementsByTagName('channelname')[0].firstChild.data
            song = channels.getElementsByTagName('songtitle')[0].firstChild.data
            artist = channels.getElementsByTagName('artist')[0].firstChild.data
            nowplaying[str(channel).strip().lower()] = {'artist': artist, 'song': song}
        sirius_xml.unlink()

        return nowplaying

    def nowPlaying(self):
        '''return a dictionary of info about whats currently playing'''
        nowplaying = {}
        channel = self.__stream['longName'].lower() 
        xml = self.getNowPlaying()
        if channel in xml:
            song = xml[channel]['song']
            artist = xml[channel]['artist']
            nowplaying['playing'] = song + ', ' + artist
        else:
            nowplaying['playing'] = 'No song/artist info for ' + channel

        nowplaying['longName'] = channel.title()
        nowplaying['logfmt'] = '%s %s: %s'%(time.strftime('%y %m|%d %H:%M'),
                                          channel.title(),nowplaying['playing'])
        if nowplaying['playing'] != self.playing:
            nowplaying['new'] = True
            self.playing = nowplaying['playing']
            logfd = open(self.playlist,'a')
            nowplayinglog = nowplaying['logfmt'].encode("utf-8")
            logfd.write("%s\n" % nowplayinglog)
            logfd.close()
        else:
            nowplaying['new'] = False
        return nowplaying
