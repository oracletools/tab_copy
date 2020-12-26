"""GUIPubSub.py
Use pubsub to control the GUI.
"""

import wx
from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub

class BasePanel(wx.Panel):
    ### This panel assures the panel has a menu
    def __init__(self, parent, *args, **kwds):
        assert 'name' in kwds, "Panel must have a name"
        self.Menu = kwds.pop('menu', None)
        if not self.Menu: self.Menu = wx.Menu()

        wx.Panel.__init__(self, parent, *args, **kwds)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(self, label="This is a panel")
        sizer.Add(self.label)
        self.SetSizer(sizer)

    def GetMenu(self):
        """Returns the menu associated with this panel"""
        return self.Menu

class BluePanel(BasePanel):
    ### Subclass BasePanel with the particulars
    def __init__(self, parent):
        blueMenu = wx.Menu()
        meanieId = wx.NewId()
        blueMenu.Append(meanieId, "Blue meanie", "It's a blue world, Max.")
        BasePanel.__init__(self, parent, menu = blueMenu, name="Blue")
        self.SetBackgroundColour("Light Blue")

        ###Menu events are processed at the frame level,
        ### but by the time the panel is created, we have
        ### a frame and a notebook, so we can get to it
        ### with GetTopLevelParent()
        ### It's better than trying to bind everything at the
        ### Frame level. do it here instead.
        top=self.GetTopLevelParent()
        top.Bind(wx.EVT_MENU, self.OnMeanie, id=meanieId)

    def OnMeanie(self, evt):
        pub.sendMessage('statusbar.update', status='Send in the Apple Bonkers!')

class RedPanel(BasePanel):
    def __init__(self, parent):
        redMenu = wx.Menu()
        redMenu.Append(wx.ID_ANY, "Red Five", "I'm going in.")
        BasePanel.__init__(self, parent, menu=redMenu, name="Red")
        self.SetBackgroundColour("Pink")
        sizer = self.GetSizer()
        aButton = wx.Button(self, label="Luke, are you okay?")
        sizer.Add(aButton)
        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.OnButton, aButton)

    def OnButton(self, evt):
        pub.sendMessage('statusbar.update', status="I'm okay but R2 is in trouble")

class MyNotebook(wx.Notebook):
    ### The notebook keeps track of pages
    ### We are subclassing to keep track of events and accept messages
    def __init__(self, parent, *args, **kwds):
        wx.Notebook.__init__(self, parent, *args, **kwds)

        bluePanel = BluePanel(self)
        redPanel = RedPanel(self)

        self.AddPage(bluePanel, bluePanel.GetName())
        self.AddPage(redPanel, redPanel.GetName())

        ### Bind events
        ### We use the page changed event to catch when the user clicks
        ### on a tab.
        ### To prevent this from happening, catch the
        ###  wx.EVT_NOTEBOOK_PAGE_CHANGING event and Veto the event if needed.
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

        ### Subscribe to messages
        pub.subscribe(self.OnChange, 'notebook.select')

    def OnPageChanged(self, evt):
        name = self.GetPageText(evt.GetSelection())
        pub.sendMessage('tabmenu.change', itemLabel=name)
        pub.sendMessage('menubar.change', itemLabel=name)
        evt.Skip()

    def OnChange(self, index):
        name = self.ChangeSelection(index-1)


class MyFrame(wx.Frame):
    def __init__(self, parent, *args, **kwds):
        wx.Frame.__init__(self, parent, *args, **kwds)
        mbar = wx.MenuBar()
        sbar = wx.StatusBar(self)

        self.Book = MyNotebook(self)

        self.SetMenuBar(mbar)
        self.SetStatusBar(sbar)
        ### Create the tab menu
        self.tabMenu = tb = wx.Menu()
        mbar.Append(tb, "&Tabs")
        ### Populate the tab menu and the menubar
        for idx in range(self.Book.GetPageCount()):
            page = self.Book.GetPage(idx)
            tb.Append(idx+1,
                      "%s\tCtrl-%d" % (page.GetName(), idx+1),
                      "Go to %s page" % (page.GetName()))
            ### Additions to the menu bar
            menu = page.GetMenu()
            mbar.Append(menu, page.GetName())

        tb.AppendSeparator()
        tb.Append(wx.ID_CLOSE, "Close\tAlt-X", "Run away ... terribly fast.")
        # Add a help menu
        hMenu = wx.Menu()
        hMenu.Append(wx.ID_ABOUT)
        mbar.Append(hMenu, "&Help")
        self.SetStatusText("Welcome",0)

        ### EVENT BINDINGS
        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnTabMenu, id=0, id2=self.Book.GetPageCount())

        ### MESSAGE SUBSCRIPTIONS
        pub.subscribe(self.OnStatusUpdate,   'statusbar.update')
        pub.subscribe(self.OnStatusClear,    'statusbar.clear')
        pub.subscribe(self.OnTabMenuMessage, 'tabmenu.change')
        pub.subscribe(self.OnMenuBarMessage, 'menubar.change')

        ### SEND INITIAL MESSAGES
        idx = self.Book.GetSelection()
        name = self.Book.GetPageText(idx)
        pub.sendMessage('tabmenu.change', itemLabel=name)
        pub.sendMessage('menubar.change', itemLabel=name)

    def OnAbout(self, evt):
        pub.sendMessage('statusbar.update', status='Bragging about this app')
        wx.MessageBox("This is my program. Muy Neato, huh?",
                      "About this App",
                      wx.OK)

    def OnClose(self, evt):
        self.Close(True)

    def OnStatusUpdate(self, status):
        self.SetStatusText(status,0)

    def OnStatusClear(self):
        self.SetStatusText('',0)

    def OnTabMenuMessage(self, itemLabel):
        ### Respond to a message to change the tabmenu
        ### Disable all tab menu items (except the close item)
        for idx in range(self.Book.GetPageCount()):
            mi = self.tabMenu.FindItemById(idx+1)
            if mi.GetLabel() == itemLabel:
                mi.Enable(False) # Don't want to be able to switch to the current page
            else:
                mi.Enable(True)
            ### Another way to do this:
            #mi.Enable(mi.GetLabel() != itemLabel)
            ### The problem with this is there are several logical steps taken in one line

    def OnMenuBarMessage(self, itemLabel):
        ### Disable all page menus but the current one
        mbar = self.GetMenuBar()
        for idx in range(self.Book.GetPageCount()):
            page = self.Book.GetPage(idx) ## returns the page
            menu = mbar.FindMenu(page.GetName())  ## returns an integer

            if page.GetName() == itemLabel:
                mbar.EnableTop(menu, True)
            else:
                mbar.EnableTop(menu, False)

    def OnTabMenu(self, evt):
        ### Get the label of the menu item
        mbar=self.GetMenuBar()
        mi = mbar.FindItemById(evt.GetId())
        ### Send the messages
        pub.sendMessage('notebook.select', index = evt.GetId())
        pub.sendMessage('menubar.change', itemLabel = mi.GetLabel())
        pub.sendMessage('tabmenu.change', itemLabel = mi.GetLabel())

class App(wx.App):
    def OnInit(self):
        frame = MyFrame(None, title="Notebook Application")
        frame.CenterOnScreen()
        self.SetTopWindow(frame)
        frame.Show()
        return True

a = App(False)
a.MainLoop()