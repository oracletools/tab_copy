import wx
import wx.grid as gridlib
class MyGrid(gridlib.Grid):
    def __init__(self, parent):
        """Constructor"""
        gridlib.Grid.__init__(self, parent)
        self.CreateGrid(2, 3)

class MyForm(wx.Frame):
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, parent=None, title="An Eventful Grid",size=(700,700))
        p = wx.Panel(self)

        button2 = wx.Button(p, -1, label="click me")
        st = wx.StaticText(p, -1,"Right-click on the panel to show a popup menu")
        p2 = wx.Panel(p, size=(400,200))
        p2.SetBackgroundColour((100, 0, 0))
        myGrid = MyGrid(p)


        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(button2)
        sizer.Add(st)
        sizer.Add(myGrid, 1, wx.EXPAND)#,pos=(200,200)
        sizer.Add(p2, 2, wx.EXPAND)
        p.SetSizer(sizer)

if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyForm().Show()
    app.MainLoop()