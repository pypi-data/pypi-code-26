# -*- coding:utf-8 -*- 
# Date: 2018-03-07 16:41:50
# Author: dekiven

import os
from DKVTools.Funcs import *

if isPython3() :
	import tkinter as tk  
	from tkinter import ttk 
	from tkinter import *
	import tkinter.filedialog as fileDialog
	import tkinter.messagebox as messageBox
else:
	import Tkinter as tk  
	import  ttk
	from Tkinter import *
	import tkFileDialog as fileDialog
	import tkMessageBox as messageBox


Pathjoin = os.path.join
PathExists = os.path.exists
# curDir = os.getcwd()
curDir = os.path.split(sys.argv[0])[0]

def getTk() :
	'''return tk, ttk
	'''
	return tk, ttk

def GetEntry(root, default='', onKey=None) :
	et = StringVar()
	entry = ttk.Entry(root, textvariable=et)
	if isFunc(onKey) :
		entry.bind('<Key>', lambda event : onKey(event.char))

	def getValue() :
		return et.get()
	def setValue(value) :
		return et.set(str(value))
	entry.getValue = getValue
	entry.setValue = setValue
	setValue(default)

	return entry


def GetDirWidget(root, title='', pathDefault='', pathSaved = None, callback = None, enableEmpty = False):
	widget = Frame(root)
	widget.columnconfigure(1, weight=1)


	strTitle = StringVar()
	strTitle.set(title)
	Label(widget, textvariable = strTitle).grid(row = 1, column = 0, padx=5)

	strPathD = StringVar()
	strPathD.set(pathDefault)
	Label(widget, textvariable = strPathD).grid(row = 0, column = 1, sticky=(N, S, W, E), pady=5)

	strTitle = StringVar()
	strTitle.set(title)
	et = StringVar()
	if pathSaved :
		et.set(pathSaved)

	Entry(widget, textvariable = et).grid(row = 1, column = 1, sticky=(N, S, W, E), pady=5)

	def btnCallback():
		def onChoosen(path):
			if path is not None and path != '' or enableEmpty :
				setValue(path)
				if callback is not None :
					if not isinstance(path, str):
						path = path
					callback(path)
		ShowChooseDirDialog(onChoosen, initialdir=et.get())


	Button(widget, text = u'Search', command = btnCallback).grid(row = 1, column = 2, padx=5)

	widget.strTitle = strTitle
	widget.strPathD = strPathD
	widget.et = et

	def setValue(value):
		et.set(value)
	widget.setValue = setValue

	return widget

def ShowChooseDirDialog(callback=None, **options):	
	'''ShowChooseDirDialog(callback=None, **options)
	callback 回调，传入选中的文件夹名
	options = {
		'defaultextension' : '.txt',
		'filetypes' : [('all files', '.*'), ('text files', '.txt')],
		'initialdir' : initDir,
		'initialfile' : 'myfile.txt',
		'parent' : root,
		'title' : 'This is a title',
	}可部分或全部不设置	
	'''
	path = fileDialog.askdirectory(**options)
	if isFunc(callback):
		# if not isinstance(path, str):
		# 	path = path
		callback(path)


def ShowChooseFileDialog(callback=None, MultiChoose=False, **options):	
	'''ShowChooseFileDialog(callback=None, MultiChoose=False, **options)
	callback 回调，传入选中的文件名Tuple
	MultiChoose 是否是多选模式
	options = {
		'defaultextension' : '.txt',
		'filetypes' : [('all files', '.*'), ('text files', '.txt')],
		'initialdir' : initDir,
		'initialfile' : 'myfile.txt',
		'parent' : root,
		'title' : 'This is a title',
	}可部分或全部不设置
	'''
	path = None
	if MultiChoose :
		path = fileDialog.askopenfilenames(**options)
	else :
		path = fileDialog.askopenfilename(**options)
	if isFunc(callback) :
		# if not isinstance(path, str):
		# 	path = path
		callback(path)

def ShowSaveAsFileDialog(callback=None, **options):
	'''ShowSaveAsFileDialog(callback=None, **options)
	callback 回调，传入保存的文件名
	options = {
		'defaultextension' : '.txt',
		'filetypes' : [('all files', '.*'), ('text files', '.txt')],
		'initialdir' : initDir,
		'initialfile' : 'myfile.txt',
		'parent' : root,
		'title' : 'This is a title',
	}可部分或全部不设置	
	'''
	path = fileDialog.asksaveasfilename(**options)
	if isFunc(callback) :
		# if not isinstance(path, str):
		# 	path = path
		callback(path)

def ShowInfoDialog(msg, title = u'Tips'):
	'''显示一个按钮的消息框。'''
	return messageBox.showinfo(title = title, message = msg)

def ShowAskDialog(msg, title = u'Asking'):
	'''显示有Yes，NO两个选项的提示框。'''
	return messageBox.askokcancel(title = title, message = msg)

def isTkWidget(widget) :
	return isinstance(widget, Widget)

def getTopLevel(widget) :
	if isTkWidget(widget) :
		return widget.winfo_toplevel()
	else :
		return None

__quitHandleFuncs = {}
def handleTopLevelQuit(widget, callback) :
	'''捕获给定widget的TopLevel的关闭事件。当TopLevel关闭时调用callback'''
	top = getTopLevel(widget)

	funcs = __quitHandleFuncs.get(str(top))
	if funcs is None :
		funcs = []
	if not callback in funcs :
		funcs.append(callback)
	__quitHandleFuncs[str(top)] = funcs

	def quit(*args, **dArgs):
		for f in funcs :
			if isFunc(f) :
				f()
		del __quitHandleFuncs[str(top)]
		top.quit()

	if top is not None and isFunc(callback) :
		top.protocol('WM_DELETE_WINDOW', quit)

# ==================鼠标Enter提示Label  begin----------------
class __ToolTip(object):
	def __init__(self, widget):
		self.widget = widget
		self.tipwindow = None
		self.x = self.y = 0

	def showtip(self, **labelConfig):
		"Display text in tooltip window"
		if self.tipwindow :
			return
		x, y, _cx, cy = self.widget.bbox("insert")
		x = x + self.widget.winfo_rootx()
		y = y + cy + self.widget.winfo_rooty() - 50
		self.tipwindow = tw = tk.Toplevel(self.widget)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))

		keys = list(labelConfig.keys())

		if 'bg' not in keys and 'background' not in keys :
			labelConfig['bg'] = '#aaaaff'
		label = tk.Label(tw, **labelConfig)
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tipwindow
		self.tipwindow = None
		if tw:
			tw.destroy()

def regEnterTip(widget, **labelConfig) :
	toolTip = __ToolTip(widget)
	def enter(event):
		toolTip.showtip(**labelConfig)
	def leave(event):
		toolTip.hidetip()
	widget.bind('<Enter>', enter)
	widget.bind('<Leave>', leave)
# ----------------鼠标Enter提示Label  end==================


# ---------------------------------------------test begin --------------------------------------------------

def __testHandleTopLevelQuit() :
	f = Frame()
	f.grid()

	l = Label(f, text='test')
	f.grid()

	def handleF() :
		print('f')

	def handleL() :
		print('l')

	handleTopLevelQuit(f, handleF)
	handleTopLevelQuit(l, handleL)

	f.mainloop()

def __testAskFile() :
	def func(*args, **dArgs) :
		print(args, dArgs)

	ShowChooseFileDialog(func)
	ShowChooseFileDialog(func, True)

def __testGetDirWid() :
	root = Tk()
	v = GetDirWidget(root, u'选择路径', 'test')
	v.pack(expand=YES, fill=BOTH)
	v.mainloop()

def __main():
	# __testAskFile()
	# __testHandleTopLevelQuit()
	__testGetDirWid()


if __name__ == '__main__':
	__main()
# ============================================test end ===========================================
