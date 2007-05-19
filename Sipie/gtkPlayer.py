#!/usr/bin/python
# -*- coding: utf-8 -*-


def gtkPlayer():
    import sys
    import os
    import gtk
    import atexit
    import gtk.glade
    from Popup import PlaylistPopup

    glade_base = os.path.split(__file__)[0]
    GLADE_DIR = os.path.join(glade_base, 'glade')

    # From Sipie
    from Config import Config
    from Player import Player
    import StreamHandler

    if sys.platform == 'win32':
        configdir = '.'
        streamHandler = StreamHandler.wmpHandler('c:\\Program Files\\Windows Media Player\\mplayer2.exe')
    else:
        configdir = '%s/.sipie' % (os.environ)['HOME']
        streamHandler = StreamHandler.mplayerHandler('/usr/bin/mplayer')

    def onExit():
       #global histfile, readline, sipie
        sipie.close()
        try:
            popups.stop()
        except:
            pass

    #histfile = os.path.join(configdir, 'history')
    config = Config(configdir)
    sipie = Player(config.items())
    sipie.setPlayer(streamHandler)
    atexit.register(onExit)


    class GladeHandlers:

        def on_Exit_clicked(widget):
            gtk.main_quit(glade_base)

        def on_Play_clicked(widget):
            global stream
            sipie.setStream(stream)
            sipie.play()

        def on_Stop_clicked(widget):
            sipie.close()

        def on_StreamList_changed(widget):
            global stream
            stream = widget.get_active_text()

        def on_window1_delete_event(widget):
            gtk.main_quit()

        def on_window1_destroy_event(widget):
            gtk.main_quit()


    xml = gtk.glade.XML(os.path.join(GLADE_DIR, 'gtkSipie.glade'))
    streamWidget = xml.get_widget('StreamList')
    #streamWidget.insert_text(0,'First')

    for selectable in sipie.getStreams():
        streamWidget.append_text(selectable)
    streamWidget.set_active(0)

    xml.signal_autoconnect(GladeHandlers.__dict__)

    popups = PlaylistPopup(sipie)
    try:
        popups = PlaylistPopup(sipie)
    except:
        print 'popups failed to load'  #DEBUG
        pass
    else:
        popups.start()

    gtk.main()


