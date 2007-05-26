# -*- coding: utf-8 -*-

def wxPlayer():
    import wx
    import sys
    import os
    import atexit
    #setuptools
    from pkg_resources import Requirement, resource_filename
    # Sipie imports
    from Config import Config
    from Player import Player
    import StreamHandler

    tryPopups = True
    if tryPopups:
        from Popup import PlaylistPopup

    def onExit(histfile,sipie):
        fd = open(histfile, 'a')
        if sipie.getStream() is not None:
            fd.write('%s\n' % sipie.getStream())
            fd.close()
        sipie.close()


    class TopFrame(wx.Frame):

        def __init__(self, *args, **kwds):
            global sipie 
            self.sipie = sipie
            streamsSorted = self.__sortStreams(self.sipie.getStreams())
            kwds['style'] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)
            self.stream_combo_box = wx.ComboBox(self, -1, choices=
                    streamsSorted, style=wx.CB_DROPDOWN | wx.CB_READONLY)
            self.play_button = wx.Button(self, -1, 'play', style=wx.BU_EXACTFIT)
            self.stop_button = wx.Button(self, -1, 'stop', style=wx.BU_EXACTFIT)
            self.exit_button = wx.Button(self, -1, 'exit', style=wx.BU_EXACTFIT)

            self.__set_properties()
            self.__do_layout()

            wx.EVT_COMBOBOX(self, self.stream_combo_box.GetId(), self.stream_combo)
            wx.EVT_BUTTON(self, self.play_button.GetId(), self.play_pressed)
            wx.EVT_BUTTON(self, self.stop_button.GetId(), self.stop_pressed)
            wx.EVT_BUTTON(self, self.exit_button.GetId(), self.exit_pressed)

        def __sortStreams(self, allstreams):
            outputStreams = []
            try:
                historyFileFD = open(histfile) 
            except IOError:
                return allstreams
            for stream in historyFileFD:
                if stream.rstrip() in allstreams:
                    outputStreams.insert(0, stream.rstrip())
            outputStreams = outputStreams + allstreams
            set = {}
           # only return uniq entrys, in order
            return [set.setdefault(e, e) for e in outputStreams if e not in 
                    set]

        def __set_properties(self):
            self.SetTitle('wxSipie')
            self.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, 
                         ''))
            self.stream_combo_box.SetSelection(0)

        def __do_layout(self):
            top_sizer = wx.BoxSizer(wx.VERTICAL)
            button_grid_sizer = wx.GridSizer(1, 3, 0, 0)
            top_sizer.Add(self.stream_combo_box, 0, wx.EXPAND | wx.ADJUST_MINSIZE, 
                          0)
            button_grid_sizer.Add(self.play_button, 0, wx.ALIGN_CENTER_HORIZONTAL | 
                                  wx.ADJUST_MINSIZE, 0)
            button_grid_sizer.Add(self.stop_button, 0, wx.ALIGN_CENTER_HORIZONTAL | 
                                  wx.ADJUST_MINSIZE, 0)
            button_grid_sizer.Add(self.exit_button, 0, wx.ALIGN_CENTER_HORIZONTAL | 
                                  wx.ADJUST_MINSIZE, 0)
            top_sizer.Add(button_grid_sizer, 1, wx.EXPAND, 0)
            self.SetAutoLayout(True)
            self.SetSizer(top_sizer)
            top_sizer.Fit(self)
            top_sizer.SetSizeHints(self)
            self.Layout()

        def stream_combo(self, event):
            stream = self.stream_combo_box.GetValue()
            event.Skip()

        def play_pressed(self, event):
            stream = self.stream_combo_box.GetValue()
            self.sipie.setStream(stream)
            self.sipie.play()
            event.Skip()

        def stop_pressed(self, event):
            self.sipie.close()
            event.Skip()

        def exit_pressed(self, event):
            self.sipie.close()
            sys.exit(0)
            event.Skip()


    # end of class TopFrame


    class SipieGui(wx.App):

        def OnInit(self):
            wx.InitAllImageHandlers()
            top_frame = TopFrame(None, -1, '')
            self.SetTopWindow(top_frame)
            top_frame.Show()
            icon_file = resource_filename(
                        Requirement.parse("Sipie"),"Sipie/data/sipie.png")
            if os.path.isfile(icon_file):
                icon = wx.Icon(icon_file, wx.BITMAP_TYPE_PNG)
                top_frame.SetIcon(icon)
            return 1


    # end of class SipieGui


    class CaptchaFrame(wx.Frame):

        def __init__(self, *args, **kwds):
            global wXcaptcha_file
            kwds['style'] = wx.DEFAULT_FRAME_STYLE
            wx.Frame.__init__(self, *args, **kwds)
            self.bitmap_captcha = wx.StaticBitmap(self, -1, wx.Bitmap(wXcaptcha_file, 
                    wx.BITMAP_TYPE_ANY))
                                 
            self.text_ctrl_captcha = wx.TextCtrl(self, -1, '', style=wx.TE_PROCESS_ENTER)
            self.captcha_button = wx.Button(self, -1, _('Enter'))

            self.__set_properties()
            self.__do_layout()

            self.Bind(wx.EVT_TEXT_ENTER, self.captcha_text_enter, self.text_ctrl_captcha)
            self.Bind(wx.EVT_BUTTON, self.captchaButton_pressed, self.captcha_button)

        def __set_properties(self):
            self.SetTitle(_('Captcha_1'))
            self.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, 
                         ''))
            self.text_ctrl_captcha.SetMinSize((85, 32))
            self.text_ctrl_captcha.SetFocus()

        def __do_layout(self):
            sizer_captcha = wx.BoxSizer(wx.VERTICAL)
            grid_sizer_captcha = wx.GridSizer(1, 2, 0, 0)
            sizer_captcha.Add(self.bitmap_captcha, 0, wx.ADJUST_MINSIZE, 
                              0)
            grid_sizer_captcha.Add(self.text_ctrl_captcha, 0, wx.ALIGN_CENTER_HORIZONTAL, 
                                   0)
            grid_sizer_captcha.Add(self.captcha_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 
                                   0)
            sizer_captcha.Add(grid_sizer_captcha, 1, wx.ALIGN_CENTER_HORIZONTAL, 
                              0)
            self.SetAutoLayout(True)
            self.SetSizer(sizer_captcha)
            sizer_captcha.Fit(self)
            sizer_captcha.SetSizeHints(self)
            self.Layout()

        def captchaButton_pressed(self, event):
            global captcha_responce
            captcha_responce = self.text_ctrl_captcha.GetValue()
            self.Close()

        def captcha_text_enter(self, event):
            global captcha_responce
            captcha_responce = self.text_ctrl_captcha.GetValue()
            self.Close()


    # end of class CaptchaFrame


    class xCaptcha(wx.App):

        def OnInit(self):
            wx.InitAllImageHandlers()
            Captcha = CaptchaFrame(None, -1, '')
            self.SetTopWindow(Captcha)
            Captcha.Show()
            return 1


    # end of class xCaptcha


    def guiCaptcha(arg):
        global wXcaptcha_file
        global captcha_responce 
        wXcaptcha_file = arg
        import gettext
        gettext.install('Captcha')  # replace with the appropriate catalog name

        Captcha = xCaptcha(0)
        Captcha.MainLoop()
        return captcha_responce

    if sys.platform == 'win32':
        configdir = '.'
        streamHandler = StreamHandler.wmpHandler('c:\\Program Files\\Windows Media Player\\mplayer2.exe')
    else:
        configdir = '%s/.sipie' % (os.environ)['HOME']
        streamHandler = StreamHandler.mplayerHandler('/usr/bin/mplayer')


    config = Config(configdir)
    histfile = os.path.join(configdir,'history')

    # check whats in config file
    missingFromConfig = []
    for XconfigItem in config.execpted:
        if XconfigItem not in config.items():
            missingFromConfig.append(XconfigItem)
    if len(missingFromConfig) > 0:
        for missed in missingFromConfig:
            print '%s option missing from config' % missed
        print 'add missing options to %s' % confile
        print 'or delete %s and rerun' % confile
        sys.exit(1)

    global sipie
    sipie = Player(config.items())
    sipie.setPlayer(streamHandler)
    atexit.register(onExit,histfile,sipie)

    if tryPopups:
        try:
            popups = PlaylistPopup(sipie)
        except:
            print 'popups failed to load'  #DEBUG
            pass
        else:
            popups.start()

    wxSipie = SipieGui(0)
    wxSipie.MainLoop()
