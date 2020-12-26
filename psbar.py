import time
import wx
#from wx.lib.pubsub import setupkwargs
#try:
#    from pubsub import pub
#except ImportError:
from wx.lib.pubsub import pub

class ListeningGauge(wx.Gauge):
    def __init__(self, *args, **kwargs):
        wx.Gauge.__init__(self, *args, **kwargs)
        pub.subscribe(self.start_listening, "progress_awake")
        pub.subscribe(self.stop_listening, "progress_sleep")

    def _update(self, this, total):
        try:
            self.SetRange(total)
            self.SetValue(this)
        except Exception as e:
            print e

    def start_listening(self, listen_to):
        rect = self.Parent.GetFieldRect(1)
        self.SetPosition((rect.x+2, rect.y+2))
        self.SetSize((rect.width-4, rect.height-4))
        self.Show()
        pub.subscribe(self._update, listen_to)

    def stop_listening(self, listen_to):
        pub.unsubscribe(self._update, listen_to)
        self.Hide()


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)

        status = self.statusbar = self.CreateStatusBar() # A StatusBar in the bottom of the window
        status.SetFieldsCount(3)
        status.SetStatusWidths([-2,200,-1])

        self.progress_bar = ListeningGauge(self.statusbar, style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
        rect = self.statusbar.GetFieldRect(1)
        self.progress_bar.SetPosition((rect.x+2, rect.y+2))
        self.progress_bar.SetSize((rect.width-4, rect.height-4))
        self.progress_bar.Hide()

        panel = wx.Panel(self)
        shortButton = wx.Button(panel, label="Run for 3 seconds")
        longButton = wx.Button(panel, label="Run for 6 seconds")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(shortButton, 0, wx.ALL, 10)
        sizer.Add(longButton, 0, wx.ALL, 10)

        panel.SetSizerAndFit(sizer)

        shortButton.Bind(wx.EVT_BUTTON, self.Run3)
        longButton.Bind(wx.EVT_BUTTON, self.Run6)

    def Run3(self, event):
        pub.sendMessage('progress_awake', listen_to = 'short_update')
        wx.BeginBusyCursor()
        for x in range(6):
            pub.sendMessage('short_update', this = x+1, total = 6)
            time.sleep(0.5)
        wx.EndBusyCursor()
        pub.sendMessage('progress_sleep', listen_to = 'short_update')

    def Run6(self, event):
        pub.sendMessage('progress_awake', listen_to = 'long_update')
        wx.BeginBusyCursor()
        for x in range(12):
            pub.sendMessage('long_update', this = x+1, total = 12)
            time.sleep(0.5)
        wx.EndBusyCursor()
        pub.sendMessage('progress_sleep', listen_to = 'long_update')


app = wx.App(False)
frame = MainWindow(None, "Listening Gauge Demo")
frame.Show(	)
app.MainLoop()
