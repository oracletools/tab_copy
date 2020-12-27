import win32gui

toplist = []
winlist = []
def enum_callback(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

print win32gui.EnumWindows(enum_callback, toplist)
print toplist
#firefox = [(hwnd, title) for hwnd, title in winlist if 'firefox' in title.lower()]
all = [(hwnd, title) for hwnd, title in winlist]
# just grab the first window that matches
all = all[0]

print all
# use the window handle to set focus
#win32gui.SetForegroundWindow(all[0])
#To minimize the window, the following line:

#import win32con
#win32gui.ShowWindow(all[0], win32con.SW_MINIMIZE)