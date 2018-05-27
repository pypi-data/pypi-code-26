"""Module tools - plotexport: Let the user create nice plots"""
import wx


class Tool(wx.Frame):
    # This tool is derived from a wx.frame.
    def __init__(self, parent):
        # parent is the main frame of PyCorrFit
        self.parent = parent
        # Get the window positioning correctly
        pos = self.parent.GetPosition()
        pos = (pos[0]+100, pos[1]+100)
        wx.Frame.__init__(self, parent=self.parent, title="Example Tool",
                 pos=pos, style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)
        ## MYID
        # This ID is given by the parent for an instance of this class
        self.MyID = None
        # Page - the currently active page of the notebook.
        self.Page = self.parent.notebook.GetCurrentPage()
        ## Content
        self.panel = wx.Panel(self)
        btnexample = wx.Button(self.panel, wx.ID_ANY, 'Example button')
        # Binds the button to the function - close the tool
        self.Bind(wx.EVT_BUTTON, self.OnClose, btnexample)
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        self.topSizer.Add(btnexample)
        self.panel.SetSizer(self.topSizer)
        self.topSizer.Fit(self)
        self.SetMinSize(self.topSizer.GetMinSize())
        #Icon
        if parent.MainIcon is not None:
            wx.Frame.SetIcon(self, parent.MainIcon)
        self.Show(True)


    def OnClose(self, event=None):
        # This is a necessary function for PyCorrFit.
        # Do not change it.
        self.parent.toolmenu.Check(self.MyID, False)
        self.parent.ToolsOpen.__delitem__(self.MyID)
        self.Destroy()


    def OnPageChanged(self, page, trigger=None):
        """
            This function is called, when something in the panel
            changes. The variable `trigger` is used to prevent this
            function from being executed to save stall time of the user.
            Forr a list of possible triggers, see the doc string of
            `tools`.
        """
        # When parent changes
        # This is a necessary function for PyCorrFit.
        # This is stuff that should be done when the active page
        # of the notebook changes.
        self.Page = page

