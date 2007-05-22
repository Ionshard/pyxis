#!/usr/bin/python
#http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/114644

import time
import threading
import pynotify

class Task( threading.Thread ):
    def __init__( self, action, loopdelay, initdelay ):
        self._action = action
        self._loopdelay = loopdelay
        self._initdelay = initdelay
        self._running = 1
        threading.Thread.__init__( self )

    def __repr__( self ):
        return '%s %s %s' % (
            self._action, self._loopdelay, self._initdelay )

    def run( self ):
        if self._initdelay:
            time.sleep( self._initdelay )
        self._runtime = time.time()
        while self._running:
            start = time.time()
            self._action()
            self._runtime += self._loopdelay
            time.sleep( max( 0, self._runtime - start ) )  

    def stop( self ):
        self._running = 0
    
class Scheduler:
    def __init__( self ):
        self._tasks = []
        
    def __repr__( self ):
        rep = ''
        for task in self._tasks:
            rep += '%s\n' % `task`
        return rep
        
    def AddTask( self, action, loopdelay, initdelay = 0 ):
        '''           task     loopdelay   initdelay 
        self.s.AddTask(self.__popup, 30.0,      0     )
        '''
        task = Task( action, loopdelay, initdelay )
        self._tasks.append( task )
    
    def StartAllTasks( self ):
        for task in self._tasks:
            task.start()
    
    def StopAllTasks( self ):
        for task in self._tasks:
            task.stop()
            task.join()

class PlaylistPopup:

    def __init__(self,sipie):
        self.s = Scheduler()
        self.sipie = sipie
        pynotify.init("Sipie")

    def __popup(self):
        playing = self.sipie.nowPlaying()
        #if playing['new'] :
        if True:
            self.notify = pynotify.Notification(playing['stream'],
                                                    playing['playing'])
            print playing['logfmt']
            self.notify.show()

    def start(self):
        #           task     loopdelay   initdelay 
        # ---------------------------------------
        self.s.AddTask(self.__popup, 30.0,      0     )
        self.s.StartAllTasks()

    def stop(self):
        self.s.StopAllTasks()
