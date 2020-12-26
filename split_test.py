import wx, random


class TDTaskBarIcon(wx.TaskBarIcon):

	def __init__(self, parent):
		wx.TaskBarIcon.__init__(self)
		self.parentApp = parent
		self.icon = wx.Icon("images/icon_glasses.png", wx.BITMAP_TYPE_PNG)
		self.SetIconImage()

	def SetIconImage(self):
		self.SetIcon(self.icon)


class Sidebar(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		# tiled background
		self.bgimage = wx.Bitmap('images/noise.png')
		wx.FutureCall(50, self.make_canvas)
		wx.EVT_SIZE(self, self.make_canvas)
		self.SetBackgroundColour((229,226,218))

	def make_canvas(self, event=None):
		dc = wx.ClientDC(self)
		brush_bmp = wx.BrushFromBitmap(self.bgimage)
		dc.SetBrush(brush_bmp)
		w, h = self.GetClientSize()
		dc.DrawRectangle(0, 0, w, h)


class Main(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		# tiled background
		self.bgimage = wx.Bitmap('images/noise.png')
		wx.FutureCall(50, self.make_canvas)
		wx.EVT_SIZE(self, self.make_canvas)
		self.SetBackgroundColour((229,226,218))
		self.SetBackgroundColour('WHITE')

	def make_canvas(self, event=None):
		dc = wx.ClientDC(self)
		brush_bmp = wx.BrushFromBitmap(self.bgimage)
		dc.SetBrush(brush_bmp)
		w, h = self.GetClientSize()
		dc.SetPen(wx.Pen("RED", 5))
		dc.DrawRectangle(0, 0, w, h)


# Create Tapedeck class
class Tapedeck(wx.Frame):

	def __init__(self, parent):
		wx.Frame.__init__(self, parent)

		self.tbicon = TDTaskBarIcon(self)  
		self.tbicon.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)

		splitter = wx.SplitterWindow(self)
		self.Sidebar = Sidebar(splitter)
		self.Main = Main(splitter)
		splitter.SplitVertically(self.Sidebar, self.Main)
		splitter.SetSashPosition(200)
		splitter.SetMinimumPaneSize(200)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(splitter, 1, wx.EXPAND)
		self.SetSizerAndFit(sizer)
		self.SetAutoLayout(True)

		self.InitUI()
		self.SetSize((800, 600))
		self.SetTitle('Tapedeck')
		self.Center()
		self.Show(True)

	def InitUI(self):

		panel = wx.Panel(self)

		# font styles
		header = wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD, False, u'Helvetica')

		# create a menubar at the top of the user frame
		menuBar = wx.MenuBar()

		# create menus
		fileMenu = wx.Menu()
		helpMenu = wx.Menu()

		# export
		export = fileMenu.Append(wx.NewId(), "&Export", "Export Playlist",
									 wx.ITEM_NORMAL)
		export.SetBitmap(wx.Bitmap('images/men_playlist.png'))

		fileMenu.AppendSeparator()

		# quit
		quit = fileMenu.Append(wx.NewId(), "&Quit\tCtrl+Q", "Quit the program",
								   wx.ITEM_NORMAL)
		quit.SetBitmap(wx.Bitmap('images/men_quit.png'))
		self.Bind(wx.EVT_MENU, self.OnQuit, quit)

		# put the file menu on the menubar
		menuBar.Append(fileMenu, "&File")

		# about tapedeck
		about = helpMenu.Append(wx.NewId(), "&About TapeDeck",
									"About TapeDeck", wx.ITEM_NORMAL)
		about.SetBitmap(wx.Bitmap('images/men_skull.png'))
		self.Bind(wx.EVT_MENU, self.OnAbout, about)

		# put the help menu on the menubar
		menuBar.Append(helpMenu, "&Help")

		# set menu bar
		self.SetMenuBar(menuBar)

		# create a status bar at the bottom of the frame
		self.CreateStatusBar()

	def OnQuit(self, e):
		self.tbicon.RemoveIcon()  
		self.tbicon.Destroy()
		self.Close()

	def OnAbout(self, e):
		self.SetStatusText("Here's your help!")


# Run the application
def main():
	deck = wx.App()
	Tapedeck(None)
	deck.MainLoop()    

if __name__ == '__main__':
	main()