import wx

from moodleteacher import MoodleConnection, MoodleAssignments

class Gui(wx.Frame):

    def __init__(self, title, moodle_assignments):
        super().__init__(parent=None, title=title)
        self.moodle_assignments = moodle_assignments
        self.init_key_event_handlers()
        self.init_ui()
        self.Centre()

    def init_key_event_handlers(self):
        randomId = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnClose, id=randomId)
        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('Q'), randomId )])
        self.SetAcceleratorTable(accel_tbl)
  
    def OnClose(self, event):
        self.Destroy()

    def init_ui(self):
        panel = wx.Panel(self)

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        vsizer = wx.BoxSizer(wx.VERTICAL)

        info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        assignments = wx.ListCtrl(panel, style= wx.LC_REPORT)
        assignments.InsertColumn(0, 'Assignment')
        assignments.InsertColumn(1, 'Course')
        assignments.InsertColumn(2, 'Deadline')
        info_sizer.Add(assignments, 1, flag=wx.EXPAND|wx.LEFT)
        students = wx.ListBox(panel)
        info_sizer.Add(students, 1, flag=wx.EXPAND|wx.LEFT)
        files = wx.ListBox(panel)
        info_sizer.Add(files, 1, flag=wx.EXPAND|wx.LEFT)
        content_box = wx.TextCtrl(panel)        
        info_sizer.Add(content_box, 3, flag=wx.EXPAND|wx.RIGHT)

        grading_sizer = wx.BoxSizer(wx.HORIZONTAL)
        grade = wx.TextCtrl(panel)
        grading_sizer.Add(grade, 1, flag=wx.LEFT)
        comment = wx.TextCtrl(panel)        
        grading_sizer.Add(comment, 3, flag=wx.RIGHT)

        vsizer.Add(info_sizer, 1, flag=wx.EXPAND|wx.TOP|wx.ALL, border=8)
        vsizer.Add(grading_sizer, 1, flag=wx.BOTTOM|wx.ALL, border=8)

        panel.SetSizer(vsizer)

        for assignment in sorted(self.moodle_assignments, key=lambda x:x.deadline):
            row_id = assignments.Append((assignment.name, assignment.course, assignment.deadline))

if __name__ == '__main__': 
    conn = MoodleConnection(interactive=True)
    print("Fetching list of assignments ...")
    assignments = MoodleAssignments(conn)
    app = wx.App()
    gui = Gui("Moodle Teacher", assignments)
    gui.Show()
    app.MainLoop()
