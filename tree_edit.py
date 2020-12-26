import wx
import  wx.gizmos   as  gizmos
import wx.lib.agw.hypertreelist as HTL

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 
                        "Main Menu", size=(1050,490))

        # set up tree structure
        #self.tree=wx.gizmos.TreeListCtrl(self, style=wx.TR_HAS_BUTTONS|wx.TR_EDIT_LABELS)
        #style=wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_ROW_LINES|wx.TR_COLUMN_LINES)

        self.tree=HTL.HyperTreeList(self, style=wx.TR_DEFAULT_STYLE|wx.TR_HAS_VARIABLE_ROW_HEIGHT)
        #        style=wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_EDIT_LABELS|)

        self.tree.AddColumn("zero", width=200)
        self.tree.AddColumn("one", width=200)
        self.tree.AddColumn("two", width=100)
        self.tree.AddColumn("three", width=100)

        self.tree.SetColumnEditable(0, False)
        self.tree.SetColumnEditable(1, True)
        self.tree.SetColumnEditable(2, True)
        self.tree.SetColumnEditable(3, True)

        parent=self.tree.AddRoot("root", -1, -1, None)

        item=self.tree.AppendItem(parent, "A", data=None)
        self.tree.SetItemText(item, "A1" , 1)
        self.tree.SetItemText(item, "A2" , 2)
        self.tree.SetItemText(item, "A3" , 3)

        item=self.tree.AppendItem(parent, "B", data=None)
        self.tree.SetItemText(item, "B1" , 1)
        self.tree.SetItemText(item, "B2" , 2)
        self.tree.SetItemText(item, "B3" , 3)

        self.tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndLabelEdit)

    def OnEndLabelEdit(self, evt):
        print "OnEndLabelEdit"
        item=evt.GetItem()
        # item=self.tree.GetCurrentItem()   # same result as evt.GetItem() 
        print "evt.GetLabel()=", evt.GetLabel()

        # only expect one column value to have changed, but do them all
        # because we can't tell which column it was.

        a=dict()

        a["zero"]=self.tree.GetItemText(item, 0)
        a["one"]=self.tree.GetItemText(item, 1)
        a["two"]=self.tree.GetItemText(item, 2)
        a["three"]=self.tree.GetItemText(item, 3)

        print "a=", a

if __name__=='__main__':
    app = wx.PySimpleApp()
    frame=MyFrame()
    frame.Show()
    app.MainLoop()