#!/usr/bin/python
# -*- coding: utf-8 -*-
# Eli Criffield < pyeli AT zendo DOT net >
# Licensed under GPLv2 See: http://www.gnu.org/licenses/gpl.txt
# TODO: function for error message checking in __getURL
# TODO: real debug support, not just comments
# TODO: gui setup of config

import cookielib
import urllib2
import urllib
import os
import sys
import re
import time

#time.time()
__version__ = '1178140820'
__author__ = 'Eli Criffield pyeli AT zendo Dot NET'

# Thanks! for the Pretty Gumbo
# Elixir and Tonic
# http://www.crummy.com/software/BeautifulSoup/
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


def CopyRights():
    print '(c)Eli Criffield <pyeliATzendoDOTnet> http://eli.criffield.net/sipie/\nLicensed under GPLv2 http://www.gnu.org/licenses/gpl.txt'
    print ''


# Define a login error class
class LoginError(Exception):
    pass


# for Authenitcation errors to sirius
class AuthError(Exception):
    pass

# for Authenitcation errors to sirius
class InvalidStream(Exception):
    pass


CopyRights()


class Factory:

    def __init__(self, options):
        """pass a dictionary of options, like whats returned form 
         SipieConf.items()
      """

        self.host = 'www.sirius.com'
        self.__headers = {'User-agent': 'Mozilla/5.0 (X11; U; %s i686; en-US; rv:1.8.0.7) eli.criffield.net/sipie Firefox/1.5.0.7' % \
                        sys.platform}
        self.token = ''
        self.bitrate = 'low'
        self.login_type = 'subscriber'
        self.username = 'WhoAmI'
        self.cryptpass = None
        self.__stream = None
        self.asxURL = None
        self.allstreams = []
        self.playing = None
        self.__captchaCallback = None  

        for (option, value) in options.items():
            setex = "self.%s = '%s'" % (option, value)
            exec setex
        if self.login_type not in ['subscriber', 'guest']:
            print 'invalid login_type in config file'
            sys.exit(420)
        txt = options['canada'].lower()
        if txt.startswith('t') or txt.startswith('y') or txt == '1':
            self.host = 'mp.siriuscanada.ca'
            self.canada = True
        else:
            self.canada = False
        self.cookiefile = os.path.join(options['configpath'],'cookies.txt')
        self.playlist = os.path.join(options['configpath'],'playlist')
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
        else:
            proxy_handler = None
        opener = urllib2.build_opener(cookie_handler, proxy_handler)
        urllib2.install_opener(opener)

    def __dbfd(self, file, data):
        """ just used for debug file output """

        dbfd = open(file, 'w')
        dbfd.write(data)
        dbfd.close()

    def printCookies(self):
        """ print the current cookies for this instance  """

        print 'cookies :'
        for (index, cookie) in enumerate(self.__cookie_jar):
            print index, '  :  ', cookie
        print 'Enter to continue:', 
        sys.stdin.readline()

    def __getURL(self, url, postdict=None):
        """ get a url, the second arg could be dictionary of 
         options for a post 
         If there is no second option use get
         This will use the cookies and tokens for this instance 
         of Sipie
         returns a file handle
      """

        if postdict:
            postdata = urllib.urlencode(postdict)
        else:
         #print "POST=",postdata #DEBUG
            postdata = None
      #print "url=",url #DEBUG
        req = urllib2.Request(url, postdata, self.__headers)
        handle = urllib2.urlopen(req)
        self.__cookie_jar.save(ignore_discard=True, ignore_expires=True)
        return handle

    def __grabURL(self, url, file, postdict=None):
        """ same as __getURL, but the second arg is a file to write 
         the contents 
         two and the optional 3rd arg is a dictionary of values 
         for a post
      """

        if postdict:
            postdata = urllib.urlencode(postdict)
        else:
         #print "POST=",postdata #DEBUG
            postdata = None
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

        url = 'http://%s/sirius/servlet/MediaPlayer' % self.host
        if self.canada:
            url = 'http://%s/sirius/ca/servlet/MediaPlayer' % self.host
      # cooke_jar.clear() makes you reauth with every startup
      #self.__cookie_jar.clear()
        handle = self.__getURL(url)
      #self.printcookies() #DEBUG
        data = handle.read()
        handle.close()
      #self.__dbfd("MediaPlayer.html",data) #DEBUG
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
        self.__grabURL('http://%s%s' % (self.host, urlofcaptcha), capcache)
      #print "http://%s%s  %s"%(self.host,urlofcaptcha,capcache) #DEBUG
      #self.printcookies() #DEBUG
      # Get a hUMan to read the captcha to us
        if self.__captchaCallback is None:
            self.__captchaCallback = self.__dCaX
        captcha = self.__captchaCallback(capcache)
        #print "captcha='%s' filename=%s"%(captcha,capcache)#DEBUG
        if os.path.isfile(capcache):
            os.unlink(capcache)

        if self.login_type == 'subscriber':
            passwdfield = 'password'
        elif self.login_type == 'guest':
            passwdfield = 'encryptedPassword'
        values = {'activity': 'login', 'type': self.login_type, 'token': self.token, 
                  'username': self.username, passwdfield: self.cryptpass, 
                  'captchaID': captchaID, 'captcha_response': captcha, 
                  'loginForm': self.login_type}
        url = 'http://%s/sirius/servlet/MediaPlayerLogin/%s' % (self.host, 
                self.login_type)
        if self.canada:
            url = 'http://%s/sirius/ca/servlet/MediaPlayerLogin/%s' % (self.host, 
                    self.login_type)
        fd = self.__getURL(url, values)
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
        url = 'http://%s/sirius/servlet/MediaPlayer' % self.host
        if self.canada:
            url = 'http://%s/sirius/ca/servlet/MediaPlayer' % self.host
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
        soup = BeautifulSoup(data)
        for catstrm in soup.findAll('option'):
            if catstrm['value'].find('|') <> -1:  # IF FOUND
                stream = catstrm['value'].split('|')[2]
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
         if it failes with an AuthError try Sipie.auth() and try again
         or use getAsxUrl
      """

        self.validateStream()

      # Get hashkey , and the url for the asx
        post = {'activity': 'selectStream', 'stream': self.__stream, 'token': self.token}
        if self.bitrate == 'high':
         #print 'high bitrate selected' #DEBUG
            post = {'activity': 'selectBitrate', 'stream': self.__stream, 
                    'bitrate': 'high', 'token': self.token}

        url = 'http://%s/sirius/servlet/MediaPlayer' % self.host
        if self.canada:
            url = 'http://%s/sirius/ca/servlet/MediaPlayer' % self.host
        hd = self.__getURL(url, post)
        data = hd.read()
        hd.close()
        if data.find('Sorry_Pg3.gif') > 0:  #IF FOUND
         #DEBUG 0
            print "Login Error: to many logins today?"
            print "     see getasxurl-DEBUG.html"
            self.__dbfd('getasxurl-DEBUG.html', data)  #DEBUG 0
            raise LoginError
      #self.printcookies() #DEBUG
      #self.__dbfd ("streamselect.html",data) #DEBUG
        soup = BeautifulSoup(data)
        try:
            asxURL = soup.find('param', {'name': 'FileName'})['value']
        except TypeError:
         #self.__dbfd("getasuxurl-ERROR.html",data) #DEBUG
         #print "\nAuth Error:, see getasuxurl-ERROR.html\n" #DEBUG
            raise AuthError
        if not asxURL.startswith('http://%s' % (self.host, )):
            asxURL = 'http://%s%s' % (self.host, asxURL)
        self.asxURL = asxURL
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

    def setStream(self, stream):
        self.validateStream(stream)
        self.__stream = stream
        self.getAsxURL()

    def getStream(self):
        return self.__stream

    def __dCaX(self,caxfile):
        ''' unused '''
        key = '''66SiiFCr2VPmh64fGfwRDWeNgCkAqa4716A3Lxbg1XhDgs72ARFUSPAQZ3kRSiNusqC8896y8I1rDkATxch8xaF7cdCgS98NRm3C3iwmkRRPaLI1R7hCW9CgYn3uUL3gA7wGEtUSs3bkxHDWyvKfyRrMYmpH3fntSq3hLBuUtjxuf4xn33VA13rcdJQr32YNYmJ3TVSE3rqimc7y2cCy1iipp9kbvj9Uq5rmcsjyJaUp7Rni5FNMsisdQ3X4c81j6kwnZyD41tGuK7r95VhmvS1ae4SRpRsG1WXPNr7GCaEcDsUIMKGLdYdnx24GCxUZnHN4mPvBah3YW4WCyAhdN5c3eSfaqLrRgiBbQnjyJ4F3gigUPVqLT89gGVSaluKTRA6c83BIY1381TKVVk8KePqvDHEWnxXtn36UFR1ltIc1yjHEe3ru7T5DHYSR1AgXSRkXrPESCtbsNQech2am4N1RPPsgnUw7CuAF1kFpVR2Tm5WkwhU6qsi6fimQlmtReWYsq6EYAHNAQbyXCef11wRUyTUSR7KPgKVw3rxGcahMYfIImNmxv3jvKgjBjsVjR3iwj5tN2R1ARk9f3bvRLCHr'''
        caxid = int(re.match('.*_(\d\d\d)\.jpg',caxfile).groups()[0])
        k1 = -(6*caxid)
        k2 = -((6*caxid)-6)
        if k2 == 0 : k2=len(key)
        #print "cax=%s id=%s %s:%s"%(key[k1:k2],caxid,k1,k2) # DEBUG
        return key[k1:k2]


    def nowPlaying(self):
        ''' return a dictionary of info about whats currently playing
        NOTE: This is based of screen scraping a _NON_ Sirius site, don't 
        be supprised if it stops working 

        I get the playlist info from dogstarradio.com (Thanks!)
        then put it on my personal servers, please don't abuse it

        I'm always looking for a new source for playlist if anyone knows 
        one
        '''
        nullplaying = {}
        nullplaying['stream'] = self.__stream
        nullplaying['playing'] = ''
        nullplaying['time'] = ''
        nullplaying['logfmt'] = ''
        nullplaying['new'] = False
        nowplaying = {}
         
        url='http://sirius.criffield.net/%s/artistTrack'%self.__stream
        try:
            fd = self.__getURL(url)
        except :
            url='http://sirius.criffield.net/%s/artistTrack' \
                             %self.__stream.lstrip('sirius')
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

        nowplaying['stream'] = self.__stream
        nowplaying['playing'] = playing
        nowplaying['time'] = time.strftime('%y %m|%d %H:%M')
        nowplaying['logfmt'] = '%s %s: %s'%(nowplaying['time'],
                                          self.__stream,playing)
        if playing != self.playing:
            nowplaying['new'] = True
            self.playing = playing
            logfd = open(self.playlist,'a')
            logfd.write("%s\n"%nowplaying['logfmt'])
            logfd.close()
        else:
            nowplaying['new'] = False
        return nowplaying
