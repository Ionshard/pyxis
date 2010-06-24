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
import htmlfixes

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    print 'see http://www.crummy.com/software/BeautifulSoup/'
    print ' to install run `easy_install BeautifulSoup`'
    print ' or if you have apt try '
    print ' apt-get install python-beautifulsoup'
    print ''
    print 'or even put just get '
    print 'http://www.crummy.com/software/BeautifulSoup/download/BeautifulSoup.py'
    print ' and put it in the current directory'
    sys.exit(420)

if 'find' not in dir(BeautifulSoup):
    stalesoup = True
    print 'you soup is stale, and not so Beautiful anymore'
    print 'please get fresher soup'
    print 'from http://www.crummy.com/software/BeautifulSoup/'
    sys.exit(421)


# Define a login error class
class LoginError(Exception):
    pass


# for Authenitcation errors to sirius
class AuthError(Exception):
    pass

# for Authenitcation errors to sirius
class InvalidStream(Exception):
    pass


class Sirius(object):
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
        self.__captchaCallback = None  
        self.__cookie_jar = None

        if self.account.login_type not in ['subscriber', 'guest']:
            print 'invalid login_type in config file'
            sys.exit(420)

        if toBool(self.account.canada):
            self.host = 'mp.siriuscanada.ca'
            self.canada = True
        else:
            self.canada = False

        self.debug = toBool(self.settings.debug)
        self.cookiefile = os.path.join(config.confpath, 'cookies.txt')
        self.playlist = os.path.join(config.confpath, 'playlist')
        self.__setupOpener()

    def __setupOpener(self):
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

    def __dbfd(self, file, data):
        """ just used for debug file output """

        dbfd = open(file, 'w')
        dbfd.write(data)
        dbfd.close()

    def __log(self, data):
        """ just used for debug log output """

        dbfd = open('debug.log', 'a')
        dbfd.write(data)
        dbfd.close()


    def sanitize(self, data):
        """ Sanitizes Data against specific errors in the Sirus HTML that
        Beautiful soup can not handle.
        ( There is also some fix about reverting some python library that 
         python 2.6 upgraded downgraded?? )
        Thanks to:
         Corey Ling kasuko@gmail.com
         http://kasuko.com 
        """
        for sub in htmlfixes.subs:
            data = re.sub(sub[0], sub[1], data)
 
        if self.debug:
            self.__log(data) #DEBUG

        return data

    def findSessionID(self):
        """ finds the session ID cookie and returns the value """
        for (index, cookie) in enumerate(self.__cookie_jar):
          if 'JSESSIONID' in cookie.name:
            return cookie.value
        return False

    def printCookies(self):
        """ print the current cookies for this instance  """

        print 'cookies :'
        for (index, cookie) in enumerate(self.__cookie_jar):
            print index, '  :  ', cookie
        print 'Enter to continue:', 
        sys.stdin.readline()

    def __getURL(self, url, postdict=None, poststring=None):
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

        if self.debug:
            self.__log("POST=%s" % postdata)#DEBUG
            self.__log("url=%s" % url) #DEBUG

        req = urllib2.Request(url, postdata, self.__headers)
        handle = urllib2.urlopen(req)
        self.__cookie_jar.save(ignore_discard=True, ignore_expires=True)
        return handle

    def __grabURL(self, url, file, postdict=None, poststring=None):
        """ same as __getURL, but the second arg is a file to write 
         the contents 
         to and the optional 3rd arg is a dictionary of values 
         for a post
      """

        if postdict:
            postdata = urllib.urlencode(postdict)
        else:
            postdata = None
        if poststring:
            postdata = poststring

        if self.debug:
            print "POST=", postdata #DEBUG
            print "url=", url #DEBUG

        req = urllib2.Request(url, postdata, self.__headers)
        handle = urllib2.urlopen(req)
        outfd = open(file, 'w')
        data = handle.read()
        outfd.write(data)
        outfd.close()
        handle.close()
        self.__cookie_jar.save(ignore_discard=True, ignore_expires=True)
        return data

    def auth(self):
        """run auth to setup all the cookies you need to get the stream
          self.__captchaCallback should be set to 
          a fuction that accepts a file name as an
          its only argument and returns text found in that image
          (as read by a huMan)

          if no function is passed it will Guess (and fail?)

        """
        #Am i authed, should be its own function really
        data = self.__getURL(
          'http://www.sirius.com/player/listen/play.action').read()
        if 'NOW PLAYING TITLE:START' in data:
          return True

        session = self.findSessionID()
        if not session:
          self.__getURL(
            'http://www.sirius.com/player/home/siriushome.action').read()
          session = self.findSessionID()
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
        data = self.__getURL(authurl, poststring=post).read()
        if '<title>SIRIUS Player' in data:
          if self.debug:
            self.__log("got valid page at: " + authurl + "\n")
          return True
        else:
          raise LoginError

    def tryGetStreams(self):
        """ Returns a list of streams avalible, if it 
         failes with AuthError, try
          Sirius.auth() first, then try again
          Or use getStreams()
      """

        allstreams = []
        url = 'http://www.sirius.com/player/listen/play.action?resizeActivity=minimize'
        hd = self.__getURL(url)
        data = hd.read()
        hd.close()
        if data.find('name="selectedStream"') == -1:  #IF NOT FOUND
            post = {'activity': 'minimize', 'token': self.token}
            hd = self.__getURL(url, post)
            data = hd.read()
            hd.close()
        if data.find('unable to log you in') <> -1:  #IF FOUND
            self.__dbfd('login-error.html', data)  #DEBUG 0
            print 'LoginError, expired account??, see login-error.html' #DEBUG 0
            raise LoginError
        if data.find('Sorry_Pg3.gif') <> -1:  #IF FOUND
            #DEBUG 0
            print '\nLoginError: to many logins today? see login-error.html'
            self.__dbfd('login-error.html', data)  #DEBUG 0
            raise LoginError
        #self.__dbfd("miniplayer.html",data) #DEBUG XXX
      #data = open('small_playing_100.html').read() # DEBUG
        data = self.sanitize(data)
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
            #print "adding stream",stream #DEBUG
                allstreams.append(stream)
        if len(allstreams) < 5:
            #print "ERROR getting streams, see streams-DEBUG.html" # DEBUG
            #self.__dbfd('streams-DEBUG.html',data)  # DEBUG
            #return defaultstreams #TESTING
            raise AuthError
        else:
            self.allstreams = allstreams
            return allstreams

    def tryGetAsxURL(self):
        """ give this the stream you want to play and this 
         will give you the
         url for the asx, play that url
         if it failes with an AuthError try Sirius.auth() and try again
         or use getAsxUrl
      """

        self.validateStream()

        postdict = { 'channelKey': self.__stream['channelKey'],
                     'genreKey': self.__stream['genreKey'],
                     'categoryKey': self.__stream['categoryKey'],
                     'selectedStream': self.__stream['selectedStream'],
                     'stopped': 'no',
                   }
        data = self.__getURL(
            'http://www.sirius.com/player/listen/play.action',
            postdict).read()

        data = self.sanitize(data)
        soup = BeautifulSoup(data)
        try:
            firstURL = soup.find('param', {'name': 'FileName'})['value']
        except TypeError:
         #self.__dbfd("getasuxurl-ERROR.html",data) #DEBUG
         #print "\nAuth Error:, see getasuxurl-ERROR.html\n" #DEBUG
            raise AuthError
        if not firstURL.startswith('http://'):
            firstURL = 'http://%s%s' % (self.host, firstURL)
        asxURL = self.__getURL(firstURL).read()
        self.asxURL = asxURL
        if self.debug:
            print asxURL
        return asxURL

    def getAsxURL(self):
        ''' Returns an the url of the asx for the self.__stream,
        Diffrent from tryGetAsxURL it will try to authticate insted of
        fail if its needs to
        '''
        try:
            url = self.tryGetAsxURL()
        except AuthError:
            self.auth()
            url = self.tryGetAsxURL()
        return url

    def getStreams(self):
        ''' Returns an the list of streams
        Diffrent from tryGeStreams it will try to authticate insted of
        fail if its needs to
        '''
        try:
            streams = self.tryGetStreams()
        except AuthError:
            self.auth()
            streams = self.tryGetStreams()
        return streams

    def validateStream(self, stream=None):
        ''' arg
                stream
                checks if its valid
           if theres no agument then it checks self.__stream'''
        if stream is None: 
            stream = self.__stream
        if len(self.allstreams) < 5:
            self.getStreams()
        if stream not in self.allstreams:
            raise InvalidStream

    def setStreamByChannel(self, channel):
        if len(self.allstreams) < 5:
            self.getStreams()
        for stream in self.allstreams:
          if stream['channelKey'] == channel:
            self.__stream = stream
            #print 'setStreamByChannel, stream:',stream #DEBUG
            self.getAsxURL()
            return
        raise InvalidStream

    def setStreamByLongName(self, longName):
        #print 'setStreamByLongName:',longName #DEBUG
        if len(self.allstreams) < 5:
            self.getStreams()
        for stream in self.allstreams:
          if stream['longName'].lower() == longName.lower():
            #print 'setStreamByLongName, stream:',stream #DEBUG
            self.__stream = stream
            self.getAsxURL()
            return
        raise InvalidStream

    def setStream(self, stream):
        self.validateStream(stream)
        self.__stream = stream
        self.getAsxURL()

    def getStream(self):
        return self.__stream

    def __dCaX(self, caxfile):
        ''' unused '''
        key = '''66SiiFCr2VPmh64fGfwRDWeNgCkAqa4716A3Lxbg1XhDgs72ARFUSPAQZ3kRSiNusqC8896y8I1rDkATxch8xaF7cdCgS98NRm3C3iwmkRRPaLI1R7hCW9CgYn3uUL3gA7wGEtUSs3bkxHDWyvKfyRrMYmpH3fntSq3hLBuUtjxuf4xn33VA13rcdJQr32YNYmJ3TVSE3rqimc7y2cCy1iipp9kbvj9Uq5rmcsjyJaUp7Rni5FNMsisdQ3X4c81j6kwnZyD41tGuK7r95VhmvS1ae4SRpRsG1WXPNr7GCaEcDsUIMKGLdYdnx24GCxUZnHN4mPvBah3YW4WCyAhdN5c3eSfaqLrRgiBbQnjyJ4F3gigUPVqLT89gGVSaluKTRA6c83BIY1381TKVVk8KePqvDHEWnxXtn36UFR1ltIc1yjHEe3ru7T5DHYSR1AgXSRkXrPESCtbsNQech2am4N1RPPsgnUw7CuAF1kFpVR2Tm5WkwhU6qsi6fimQlmtReWYsq6EYAHNAQbyXCef11wRUyTUSR7KPgKVw3rxGcahMYfIImNmxv3jvKgjBjsVjR3iwj5tN2R1ARk9f3bvRLCHr'''
        caxid = int(re.match('.*_(\d\d\d)\.jpg', caxfile).groups()[0])
        k1 = -(6*caxid)
        k2 = -((6*caxid)-6)
        if k2 == 0:
            k2 = len(key)
        print "ca=%s cax=%s id=%s %s:%s" % (caxfile, key[k1:k2],caxid,k1,k2) # DEBUG
        return key[k1:k2]

    def terminalCaptcha(self, captchaFile):
        print "There is a captcha file, Please open the file %s" % captchaFile
        print "And input the leters below"
        return raw_input(": ")


    def nowPlaying(self):
        ''' return a dictionary of info about whats currently playing
        NOTE: This is based of screen scraping a _NON_ Sirius site, dont
        be supprised if it stops working 

        I get the playlist info from dogstarradio.com (Thanks!)
        then put it on my personal servers, please dont abuse it

        Im always looking for a new source for playlist if anyone knows 
        one
        '''
        nullplaying = {}
        nullplaying['stream'] = ''
        nullplaying['playing'] = ''
        nullplaying['time'] = ''
        nullplaying['logfmt'] = ''
        nullplaying['new'] = False
        nowplaying = {}
        
        url = 'http://sirius.criffield.net/%s/artistTrack' % self.__stream['channelKey']
        try:
            fd = self.__getURL(url)
        except:
            url = ('http://sirius.criffield.net/%s/artistTrack' %
                   (self.__stream['channelKey'].lstrip('sirius')))
            playing = None
            try:
                fd = self.__getURL(url)
            except :
                playing = None
            else:
                playing = fd.read()
                fd.close()
        else:
            playing = fd.read()
            fd.close()

        #print playing,url #DEBUG
        if playing == None:
            nowplaying = nullplaying
            self.playing = ''
            return nowplaying

        nowplaying['stream'] = self.__stream['channelKey']
        nowplaying['longName'] = self.__stream['longName'].title()
        nowplaying['playing'] = playing
        nowplaying['logfmt'] = '%s %s: %s'%(time.strftime('%y %m|%d %H:%M'),
                                          self.__stream['channelKey'],playing)
        if playing != self.playing:
            nowplaying['new'] = True
            self.playing = playing
            logfd = open(self.playlist,'a')
            logfd.write("%s\n"%nowplaying['logfmt'])
            logfd.close()
        else:
            nowplaying['new'] = False
        return nowplaying
