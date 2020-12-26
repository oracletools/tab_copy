import wx

# I normally import from garlicsim_wx since I bundle the SVN version of
# hypertreelist there:
# from garlicsim_wx.widgets.general_misc.third_party import hypertreelist
from wx.lib.agw import hypertreelist


class Frame(wx.Frame):
    def __init__(self, parent, *args, **kwargs):
        wx.Frame.__init__(self, parent, *args, **kwargs)

        self.hypertreelist = hypertreelist.HyperTreeList(
            self,
            style=wx.SIMPLE_BORDER,
            agwStyle=(
                wx.TR_FULL_ROW_HIGHLIGHT | \
                wx.TR_ROW_LINES | \
                wx.TR_HIDE_ROOT | \
                hypertreelist.TR_NO_HEADER
            )
        )
        
        
        self.hypertreelist.Bind(wx.EVT_TREE_ITEM_MENU, self.on_tree_item_menu)
        self.hypertreelist.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)

        self.hypertreelist.AddColumn('')
        self.hypertreelist.SetMainColumn(0)
        self.hypertreelist.root_item = self.hypertreelist.AddRoot('')


        self.hypertreelist.AppendItem(self.hypertreelist.root_item, 'boom',
        ct_type=1)

        self.hypertreelist.AppendItem(self.hypertreelist.root_item, 'bam',
        ct_type=2)

        self.hypertreelist.AppendItem(self.hypertreelist.root_item, 'pow',
        ct_type=2)
        
        
        self.Show()
        
        
    def on_tree_item_menu(self, event):
        print(event.GetItem())

        
    def on_context_menu(self, event):
        print('Generic context menu raised')

        
app = wx.App()
frame = Frame(None)
app.MainLoop()
