#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
ZetCode wxPython tutorial

In this code example, we create a
custom dialog.

author: Jan Bodnar
website: www.zetcode.com
last modified: July 2012
'''

import wx

class AssumeZerosDialog(wx.Dialog):
    
    def __init__(self, *args, **kw):

        self.ID_HIMAR1 = wx.NewId()
        self.ID_TN5 = wx.NewId()
           
        wx.Dialog.__init__(self, None, title="Dialog") 

        self.ID_HIMAR1 = wx.NewId()
        self.ID_TN5 = wx.NewId()

        self.SetSize((500, 300))
        self.SetTitle("Warning:  Wig Files Do Not Include Empty Sites")

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(mainSizer)

        warningText = """

One or more of your .wig files does not include any empty sites (i.e. sites with zero read-counts). The analysis methods in TRANSIT require knowing ALL possible insertion sites, even those without reads.
    
    Please indicate how you want to proceed:

    As Himar1: You will need to provide the DNA sequence (.fasta format) and TRANSIT will automatically determine empty TA sites.

    As Tn5: TRANSIT will assume all nucleotides are possible insertion sites. Those not included in the .wig file are assumed to be zero.
    """
        warningStaticBox = wx.StaticText(self, wx.ID_ANY, warningText, (-1,-1), (-1, -1), wx.ALL)
        warningStaticBox.Wrap(480)
        mainSizer.Add(warningStaticBox)
       
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        himar1Button = wx.Button(self, self.ID_HIMAR1, label='Proceed as Himar1')
        tn5Button = wx.Button(self, self.ID_TN5, label='Proceed as Tn5')
        cancelButton = wx.Button(self, wx.ID_CANCEL, label='Cancel')

        
        #button_sizer.Add(warningStaticBox)
        button_sizer.Add(himar1Button, flag=wx.LEFT, border=5)
        button_sizer.Add(tn5Button, flag=wx.LEFT, border=5)
        button_sizer.Add(cancelButton, flag=wx.LEFT, border=5)

        mainSizer.Add(button_sizer, 
            flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        
        himar1Button.Bind(wx.EVT_BUTTON, self.OnClose)
        tn5Button.Bind(wx.EVT_BUTTON, self.OnClose)
        cancelButton.Bind(wx.EVT_BUTTON, self.OnClose)
        
        
    def OnClose(self, event):

        if self.IsModal():
            self.EndModal(event.EventObject.Id)
        else:
            self.Close()        
        
        
        
class Example(wx.Frame):
    
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
        dlg = AssumeZerosDialog()
        res = dlg.ShowModal()
        print "RESULT", res
        if res == dlg.ID_HIMAR1:
            print "You chose Himar1"
        elif res == dlg.ID_TN5:
            print "You chose Tn5"
        else:
            print "You quit."
        dlg.Destroy()



if __name__ == '__main__':
    app = wx.App(False)
    ex = Example()
    app.MainLoop()
