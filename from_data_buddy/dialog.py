import wx

########################################################################
class MyDialog(wx.Dialog):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Dialog")

        self.comboBox1 = wx.ComboBox(self, 
                                     choices=['test1', 'test2'],
                                     value="")
        okBtn = wx.Button(self, wx.ID_OK)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.comboBox1, 0, wx.ALL|wx.CENTER, 5)
        sizer.Add(okBtn, 0, wx.ALL|wx.CENTER, 5)
        self.SetSizer(sizer)

########################################################################
class MainProgram(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="Main Program")
        panel = wx.Panel(self)

        btn = wx.Button(panel, label="Open dialog")
        btn.Bind(wx.EVT_BUTTON, self.onDialog)

        self.Show()

    #----------------------------------------------------------------------
    def onDialog(self, event):
        """"""
        dlg = MyDialog()
        res = dlg.ShowModal()
        if res == wx.ID_OK:
            print dlg.comboBox1.GetValue()
        dlg.Destroy()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainProgram()
    app.MainLoop()