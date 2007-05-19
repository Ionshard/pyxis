#!/usr/bin/python
# from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496800
import thread
import threading
import atexit


class Operation(threading._Timer):
    def __init__(self, *args, **kwargs):
        threading._Timer.__init__(self, *args, **kwargs)
        self.setDaemon(True)

    def run(self):
        while True:
            self.finished.clear()
            self.finished.wait(self.interval)
            if not self.finished.isSet():
                self.function(*self.args, **self.kwargs)
            else:
                return
            self.finished.set()

class Manager(object):

    ops = []

    def __init__(self):
        atexit.register(self.__onExit)

    def add_operation(self, operation, interval, args=[], kwargs={}):
        op = Operation(interval, operation, args, kwargs)
        self.ops.append(op)
        thread.start_new_thread(op.run, ())

    def stop(self):
        for op in self.ops:
            op.cancel()
        #self._event.set()

    def __onExit(self):
        self.stop()

class PlaylistPopup:
    
    def __init__(self,sipie):
        import pynotify
        self.pynotify = pynotify
        self.sipie = sipie
        self.notify = None
        self.pynotify.init("Sipie")
        self.timer = Manager()

    def start(self):
        self.timer.add_operation(self.__popup, 30)

    def __popup(self):
        playing = self.sipie.nowPlaying()
        if playing['new'] :
            self.notify = self.pynotify.Notification(playing['stream'],
                                                    playing['playing'])
            print playing['logfmt']
            self.notify.show()

    def stop(self):
        self.timer.stop()


