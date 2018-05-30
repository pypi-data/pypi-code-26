import csv
import time

import threading
import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
    import Queue as queue
    from exceptions import Exception, RuntimeError
else:
    import tkinter as tk
    import queue

import numpy as np
import matplotlib as mpl
mpl.use("TkAgg") # needs to be there
from matplotlib.backends import backend_tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.widgets import RadioButtons, RectangleSelector

class namespace:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
class HelpButton(tk.Frame):
    def __init__(self, parent, help_text='NA', *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.help_text = help_text
        
        self.button = tk.Button(self, text='Help', command=self.pop_help)
        self.button.pack()
        
    def pop_help(self):
        try:
            if self.win0.winfo_exists():
                self.win0.destroy()
        except AttributeError:
            # win0 doesn't exist so don't need to destroy it
            pass
        self.win0 = tk.Toplevel(master=self)
        self.win0.geometry('640x480')
        self.text = tk.Text(self.win0)
        self.text.pack(side='top',fill='both',expand=False)
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, self.help_text)
        self.text.config(state=tk.DISABLED)
        
class RadioOption(tk.Frame):
    def __init__(self, parent, options, command=None, default=None, *args, **kwargs):
        ''' 
        options must be a list of strings and each string has to be a valid python variable name
        '''
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.options = options
        self.default = default
        self.command = command
        
        self.var = tk.StringVar(master=self.parent)
        
        if default is not None:
            self.var.set(default) # select default option
                 
        for option in self.options:
            rb_str = 'rb_'+option
            setattr(self,rb_str,tk.Radiobutton(
            master=self, text=option, variable=self.var, value=option,command=command))
            getattr(self,rb_str).pack(side='top',anchor='w')
                
class OptionsParser(tk.Frame):
    def __init__(self, parent, target=None, initial_text='', include_button=True, on_submit=None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        if target is None:
            self.target = self.parent
        else: self.target = target
        self.on_submit = on_submit
        
        if include_button:
            self.button = tk.Button(master=self, text='Submit', command=self.submit)
            self.button.pack(side='left')
        
        self.entry = tk.Entry(master=self,width=500)
        self.entry.insert(0, initial_text)
        self.entry.pack(side='left')
    
    def submit(self):
        todict = lambda **kwargs: kwargs
        text = self.entry.get()
        in_dict = eval('todict('+text+')')
        for key in in_dict:
            setattr(self.target, key, in_dict[key])
        
        if self.on_submit is not None:
            self.on_submit(self)
        
class KillButton(tk.Frame):
    def __init__(self, parent, target, text='Kill', *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.target = target
        
        self.button = tk.Button(master=self, text=text, command=self.Kill)
        self.button.pack(side='left')
        
    def Kill(self):
        self.target.destroy()
        
class AxisLimit(tk.Frame):
    def __init__(self, parent, target, text='', *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.title_label = tk.Label(master=self,text=text)
        self.target = target
        
        self._group1 = tk.Frame(self)
        self._group1a = tk.Frame(self._group1)
        self._group1b = tk.Frame(self._group1)
        self._group2 = tk.Frame(self)
        
        self.button = tk.Button(master=self._group1, text='Submit',command=self.submit)
        
        self.max_label = tk.Label(master=self._group1a,text='max')
        self.max_entry = tk.Entry(master=self._group1a,width=7)
        self.max_label.pack(side='top')
        self.max_entry.pack(side='top')
        
        self.min_label = tk.Label(master=self._group1b,text='min')
        self.min_entry = tk.Entry(master=self._group1b,width=7)
        self.min_label.pack(side='top')
        self.min_entry.pack(side='top')
        
        self._group1b.pack(side='left')
        self._group1a.pack(side='left')
        self.button.pack(side='left',anchor='sw')
               
        self.rb_mode = RadioOption(self._group2,['automatic','manual'],default='automatic')
        self.rb_mode.pack(side='top')
        
        self.title_label.pack(anchor='w')
        self._group2.pack(anchor='w')
        self._group1.pack(anchor='w') 
        
    def submit(self):
        self.target[0] = float(self.min_entry.get())
        self.target[1] = float(self.max_entry.get())
        
class GraphFrame(tk.Frame):
    def __init__(self, parent, graph, title=None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.graph = graph
        self.parent = parent
        
        self.canvas = FigureCanvasTkAgg(self.graph, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.graph.canvas.draw()
        
        self.title_label = tk.Label(self,text=title)
        
        self.title_label.pack(side="top",anchor='c')
        self.canvas_widget.pack(side="top")
        
class MyFigure(mpl.figure.Figure):
    def __init__(self, *args, **kwargs):
        mpl.figure.Figure.__init__(self, *args, **kwargs)
        self.ax = self.add_subplot(111)
        self.line, = self.ax.plot([],[])
        
class DoubleSubplot(mpl.figure.Figure):
    def __init__(self, *args, **kwargs):
        mpl.figure.Figure.__init__(self, *args, **kwargs)
        self.ax1 = self.add_subplot(211)
        self.line1, = self.ax1.plot([],[])
        self.ax2 = self.add_subplot(212)
        self.line2, = self.ax2.plot([],[])
        
class PeakLabels(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.peak_range_var = tk.StringVar()
        self.peak_loc_var = tk.StringVar()
        self.peak_time_var = tk.StringVar()
        self.peak_height_var = tk.StringVar()
        
        self.peak_range = tk.Label(self, textvariable=peak_range_var)
        self.peak_loc = tk.Label(self, textvariable=peak_loc_var)
        self.peak_time = tk.Label(self, textvariable=peak_time_var)
        self.peak_height = tk.Label(self, textvariable=peak_height_var)
        
        self.peak_range.pack()
        self.peak_loc.pack()
        self.peak_time.pack()
        self.peak_height.pack()
    
    def update(self, peak_range, peak_loc, peak_time, peak_height):
        self.peak_range_var.set(str(peak_range))
        self.peak_loc_var
        
# class MyRectSelec(mpl.widgets.RectangleSelector):
    # def __init__(self, *args, **kwargs):
        # mpl.widgets.RectangleSelector.__init__(self, *args, **kwargs)
        
class PlotWindow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        
    def destroy(self):
        'destroying the plot window should also turn off rectselects'
        #self.master.graph1.ax1.RS0.set_visible(False)
        #self.master.graph1.ax1.RS2.set_visible(False)
        tk.Toplevel.destroy(self)
        
class MainApplication(tk.Frame):
    # the parent of this must be of type tkinter.Tk (i.e. have mainloop() and after())
    def __init__(self, parent, omc_chan, pzt_chan, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        
        self.parent = parent
        self.omc_chan = omc_chan
        self.pzt_chan = pzt_chan
        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self.pull_channels_loop)
        self.worker.daemon = True
        
        ########################################################################################
        
        self.duration = None
        self.advance_step = 1
        self.ti = None
        self.recording = False
        self.q = 8
        self.pzt_lim = [-10,120]
        self.omc_lim = [1e-5,0.6]
        self.yscale = 'linear'
        self.lowpass = False
        self.pzt_filter = True
        self.kill_time = 1
        self.dark_level = -2e-4
        #self.draw_speed = 0.5
        #self.valid_boxes = False
        self.m_range = 500
        
        self.zeroth = namespace()
        self.zeroth.x = [0,0]
        self.zeroth.y = [0,0]
        
        self.first = namespace()
        self.first.x = [0,0]
        self.first.y = [0,0]
        
        self.second = namespace()
        self.second.x = [0,0]
        self.second.y = [0,0]
        
        self.a00s = []
        self.a01s = []
        self.a02s = []
        
        self.mismatches = []
        self.t_mismatches = []
        
        self.misalignments = []
        self.t_misalignments = []
        
        ########################################################################################
        
        self.graph0 = DoubleSubplot()
        self.graph0.ax1.set_ylabel('PZT voltage [counts]')
        self.graph0.ax2.set_xlabel('Time [sec]')
        self.graph0.ax2.set_ylabel('OMC DCPD [counts]') 
        
        self.graph1 = DoubleSubplot()
        self.graph1.ax1.set_xlabel('PZT voltage [counts]')
        self.graph1.ax1.set_ylabel('OMC DCPD [counts]') 
        self.graph1.ax2.set_xlabel('Time [sec]')
        self.graph1.ax2.set_ylabel('$P_2\ / \ P_1 $')
        
        self.graph1.line3, = self.graph1.ax2.plot([],[])
              
        self.row2 = tk.Frame(self)
        self.graph_group = tk.Frame(self)

        self.graph00 = MyFigure()
        canvas00 = FigureCanvasTkAgg(self.graph00,master=self.graph_group).get_tk_widget()
        self.graph00.set_size_inches(3,3)
        self.graph00.tight_layout()
        self.graph00.line2, = self.graph00.ax.plot([],[])
        
        self.graph01 = MyFigure()
        canvas01 = FigureCanvasTkAgg(self.graph01,master=self.graph_group).get_tk_widget()
        self.graph01.set_size_inches(3,3)
        self.graph01.tight_layout()
        self.graph01.line2, = self.graph01.ax.plot([],[])
        
        #rectprops0 = dict(facecolor='red', edgecolor = 'black', alpha=0.2, fill=True)
        #self.graph1.ax1.RS0 = RectangleSelector(self.graph1.ax1, self.RS0_event, button=[1, 3],rectprops=rectprops0)
        #self.graph1.ax1.RS0.set_active(False)
        
        self.graph02 = MyFigure()
        canvas02 = FigureCanvasTkAgg(self.graph02,master=self.graph_group).get_tk_widget()
        self.graph02.set_size_inches(3,3)
        self.graph02.tight_layout()
        self.graph02.line2, = self.graph02.ax.plot([],[])
        
        self.graphframe00 = GraphFrame(self.graph_group,graph=self.graph00,title='TEM0')
        self.acquire00button = tk.Button(master=self.graphframe00,text='aquire TEM0',command=lambda: self.graph1.ax1.RS0.set_active(True))
        self.acquire00button.pack()
        self.graphframe01 = GraphFrame(self.graph_group,graph=self.graph01,title='TEM1')
        self.acquire01button = tk.Button(master=self.graphframe01,text='aquire TEM1',command=lambda: self.graph1.ax1.RS1.set_active(True))
        self.acquire01button.pack()
        self.graphframe02 = GraphFrame(self.graph_group,graph=self.graph02,title='TEM2')
        self.acquire02button = tk.Button(master=self.graphframe02,text='aquire TEM2',command=lambda: self.graph1.ax1.RS2.set_active(True))
        self.acquire02button.pack()
        
        help_text = \
'''Instructions for acquiring 0,0 peak:
    While focused on the OMC scan window hit the 'q' key to enter 0,0 select mode. 
    Draw a red box by holding down the mouse button around the location of what looks like a 0,0 peak.
    
Instructions for aquiring first order peak:
    While focused on the OMC scan window hit the 'a' key to enter 0,1 select mode. 
    Draw a blue box by holding down the mouse button around the location of the first peak.
    
Instructions for aquiring second order peak:
    While focused on the OMC scan window hit the 'z' key to enter 0,2 select mode. 
    Draw a blue box by holding down the mouse button around the location of the second peak.
    
Upon the release of the mouse button in select mode the x coordinates of the box are recorded and the selection is plotted in the main window.
    
After both selections have been made the ratio of the heights of the second peak to the 0,0 peak will be computed and plotted on the bottom subplot of the Pop 1 window.
        '''
        
        self.row1 = tk.Frame(self)
        self.graphframe0 = GraphFrame(self,graph=self.graph0)
        self.graphframe1 = GraphFrame(self,graph=self.graph1)
        
        self.button_group = tk.Frame(self.row1)
        self.killbutton = KillButton(self.button_group,target=self.parent,text='Save & Quit')
        self.pop0button = tk.Button(master=self.button_group,text='Show PZT and OMC DCPD channels',command=self.pop_0)
        self.pop1button = tk.Button(master=self.button_group,text='Show OMC scan',command=self.pop_1)
        self.helpbutton = HelpButton(self.button_group,help_text=help_text)
        
        self.lim_opts = tk.Frame(self.row1)
        self.xlim_opts = AxisLimit(parent=self.lim_opts,target=self.pzt_lim,text='PZT axis limits')
        self.xlim_opts.min_entry.insert(0,str(self.pzt_lim[0]))
        self.xlim_opts.max_entry.insert(0,str(self.pzt_lim[1]))
        self.xlim_opts.min_entry.bind('<Return>',lambda event: self.xlim_opts.submit())
        self.xlim_opts.max_entry.bind('<Return>',lambda event: self.xlim_opts.submit())
        self.xlim_opts.pack(side='left',padx=15)

        self.ylim_opts = AxisLimit(parent=self.lim_opts,target=self.omc_lim,text='OMC axis limits')
        self.ylim_opts.min_entry.insert(0,str(self.omc_lim[0]))
        self.ylim_opts.max_entry.insert(0,str(self.omc_lim[1]))
        self.ylim_opts.min_entry.bind('<Return>',lambda event: self.ylim_opts.submit())
        self.ylim_opts.max_entry.bind('<Return>',lambda event: self.ylim_opts.submit())
        self.ylim_opts.pack(side='left',padx=15)
        
        self.axscale_opts = tk.Frame(self.row1)
        self.axscale_label = tk.Label(self.axscale_opts,text='Axis Scale')
        self.rb_axscale = RadioOption(self.axscale_opts,['linear','semilogy'],default='linear')
        self.axscale_label.pack()
        self.rb_axscale.pack()
        
        self.pop0button.pack(side="top",anchor='w')
        self.pop1button.pack(side="top",anchor='w')
        self.helpbutton.pack(side="top",anchor='w')
        self.killbutton.pack(side="top",fill="both", expand=False)
        
        self.button_group.pack(side='left',anchor='n')
        self.lim_opts.pack(side='left',padx=15,anchor='n')
        self.axscale_opts.pack(side="left",anchor='n',padx=15)
        
        self.advanced_opt_frame = tk.Frame(self)
        
        self.rb_options_mode = RadioOption(self,['simple','advanced'],default='simple',command=self.show_advanced_opts)
        self.rb_pzt_filter = RadioOption(self.advanced_opt_frame,['filter','no_filter'],default='filter')
        self.optionsparser = OptionsParser(self.advanced_opt_frame,on_submit=None,target=self)
        self.optionsparser.entry.bind('<Return>',lambda event: self.optionsparser.submit())
        
        ##### Packing

        self.row1.pack(side='top',fill='both',padx=10,pady=20)
        
        # self.graphframe2.pack(side="left", padx=10, expand=False)
        # self.graphframe3.pack(side="left", padx=100, expand=False)
        
        self.graphframe00.pack(side="left", fill='both', expand=True)
        self.graphframe01.pack(side="left", fill='both', expand=True)
        self.graphframe02.pack(side="left", fill='both', expand=True)
        self.graph_group.pack(side="top", fill='both', expand=False ,padx=10,pady=20)
        
        self.rb_options_mode.pack(side="top",fill="both", expand=False)
        self.rb_pzt_filter.pack(side="left")

        self.advanced_opt_frame.pack(side="top",fill="both", expand=False)
        self.optionsparser.pack(side="top",fill="both", expand=False)
        
        ########################################################################################
    def show_advanced_opts(self):
        # print('hit',self.rb_options_mode.var.get())
        if self.rb_options_mode.var.get() == 'simple':
            self.advanced_opt_frame.pack_forget()
        else:
            self.advanced_opt_frame.pack(side="top",fill="both", expand=False)    
        
    def start(self):
        self.show_advanced_opts()
        initial_text = 'duration={0}, pzt_lim={1}, omc_lim={2}, q={3}, kill_time={4}, dark_level={5}, advance_step={6}, m_range={7}'\
        .format(self.duration, self.pzt_lim, self.omc_lim, self.q, self.kill_time, self.dark_level, self.advance_step, self.m_range)
        self.optionsparser.entry.insert(0,initial_text)
        self.worker.start()
        self.after(1, self.check_queue)        
        #self.unlock_record()
        
        # self.pop_0()
        # self.pop_1()
        
    def unlock_record(self):
        self.recording = True
        # schedule the recording to unlock in duration seconds
        self.unlock_thread = threading.Timer(self.duration,self.unlock_record)
        self.unlock_thread.daemon = True
        self.unlock_thread.start()
        
    def dict2csv(self,mydict,filename):
        with open(filename+'.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            keys = list(mydict.keys())
            writer.writerow(keys)
            for row in zip(*mydict.values()):
                writer.writerow(row)
        
    def destroy(self):
        timestamp =  str(int(time.time())) #gives unix time
    
        mismatch_dict = dict(time=self.t_mismatches,A2_A0=self.mismatches)
        self.dict2csv(mismatch_dict,timestamp+'_mismatch')
        
        misalign_dict = dict(time=self.t_misalignments,A2_A0=self.misalignments)
        self.dict2csv(misalign_dict,timestamp+'_misalign')
        
        a00s_dict = dict(time=[x[0] for x in self.a00s],a00=[x[1] for x in self.a00s])
        a01s_dict = dict(time=[x[0] for x in self.a01s],a01=[x[1] for x in self.a01s])
        a02s_dict = dict(time=[x[0] for x in self.a02s],a02=[x[1] for x in self.a02s])
        
        self.dict2csv(a00s_dict,timestamp+'_a00s')
        self.dict2csv(a01s_dict,timestamp+'_a01s')
        self.dict2csv(a02s_dict,timestamp+'_a02s')

        print('written all recorded data under '+timestamp)

        tk.Frame.destroy(self)
        
    def RS0_event(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.zeroth.x = [x1,x2]
        self.zeroth.y = [y1,y2]
        # def update_coords_entry():
            # e_02.delete(0,Tk.END)
            # e_02.insert(0,'x=[%3.2f,%3.2f],y=[%3.2f,%3.2f]' % (x1,x2,y1,y2))           
        # self.on_main_thread(update_coords_entry)
        
        self.graph1.ax1.RS0.set_active(False)
        #self.graph1.ax1.RS0.set_visible(True)
        
    def RS1_event(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.first.x = [x1,x2]
        self.first.y = [y1,y2]      
        self.graph1.ax1.RS1.set_active(False)
        
    def RS2_event(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.second.x = [x1,x2]
        self.second.y = [y1,y2]
        # def update_coords_entry():
            # e_02.delete(0,Tk.END)
            # e_02.insert(0,'x=[%3.2f,%3.2f],y=[%3.2f,%3.2f]' % (x1,x2,y1,y2))           
        # self.on_main_thread(update_coords_entry)
        
        self.graph1.ax1.RS2.set_active(False)
        #self.graph1.ax1.RS2.set_visible(True)
        
    def toggle_selector(self,event):
        print(' Key pressed.')
        if event.key in ['Q', 'q'] and not self.graph1.ax1.RS0.active:
            print(' RectangleSelector activated.')
            self.graph1.ax1.RS0.set_active(True)
        if event.key in ['W', 'w'] and self.graph1.ax1.RS0.active:
            print(' RectangleSelector deactivated.')
            self.graph1.ax1.RS0.set_active(False)
        if event.key in ['A', 'a'] and not self.graph1.ax1.RS1.active:
            print(' RectangleSelector activated.')
            self.graph1.ax1.RS1.set_active(True)
        if event.key in ['S', 's'] and not self.graph1.ax1.RS1.active:
            print(' RectangleSelector activated.')
            self.graph1.ax1.RS1.set_active(False)
        if event.key in ['Z', 'z'] and not self.graph1.ax1.RS2.active:
            print(' RectangleSelector activated.')
            self.graph1.ax1.RS2.set_active(True)
        if event.key in ['X', 'x'] and not self.graph1.ax1.RS2.active:
            print(' RectangleSelector activated.')
            self.graph1.ax1.RS2.set_active(False)
        if event.key in ['D', 'd']:
            self.graph1.ax1.RS0.set_active(False)
            self.graph1.ax1.RS1.set_active(False)
            self.graph1.ax1.RS2.set_active(False)
            #self.graph1.ax1.RS0.set_visible(False)
            #self.graph1.ax1.RS2.set_visible(False)
            self.zeroth.x = [0,0]
            self.zeroth.y = [0,0]
            self.first.x = [0,0]
            self.first.y = [0,0]
            self.second.x = [0,0]
            self.second.y = [0,0]
        
    def pop_0(self):
        try:
            if self.win0.winfo_exists():
                self.win0.destroy()
        except AttributeError:
            pass
        self.win0 = tk.Toplevel(master=self)
        canvas0 = FigureCanvasTkAgg(self.graph0,master=self.win0).get_tk_widget()
        canvas0.pack(side="top",fill="both", expand=True)
        
    def pop_1(self):
        try:
            if self.win1.winfo_exists():
                self.win1.destroy()
        except AttributeError:
            pass
        self.win1 = PlotWindow(master=self)
        
        self.canvas1 = FigureCanvasTkAgg(self.graph1,master=self.win1).get_tk_widget()
        self.canvas1.pack(side="top",fill="both", expand=True)
        
        def onselect(RS, click, event):
            pass
        
        rectprops0 = dict(facecolor='red', edgecolor = 'black', alpha=0.2, fill=True)
        self.graph1.ax1.RS0 = RectangleSelector(self.graph1.ax1, self.RS0_event, button=[1, 3],rectprops=rectprops0)
        self.graph1.ax1.RS0.set_active(False)
        
        rectprops1 = dict(facecolor='green', edgecolor = 'black', alpha=0.2, fill=True)
        self.graph1.ax1.RS1 = RectangleSelector(self.graph1.ax1, self.RS1_event,button=[1, 3],rectprops=rectprops1)
        self.graph1.ax1.RS1.set_active(False)
        
        rectprops2 = dict(facecolor='blue', edgecolor = 'black', alpha=0.2, fill=True)
        self.graph1.ax1.RS2 = RectangleSelector(self.graph1.ax1, self.RS2_event,button=[1, 3],rectprops=rectprops2)
        self.graph1.ax1.RS2.set_active(False)
        
        self.graph1.canvas.mpl_connect('key_press_event', self.toggle_selector)        
        
    def check_queue(self):
        while True:
            try:
                task = self.queue.get(block=False)
                # print('got task ', task)
                # if q is full it will raise queue.Empty
            except queue.Empty:
                # print('empty queue')
                break
            else:
                # print('running task')
                # execute task() when the gui is idle
                self.after_idle(task)
        # print('scheduling next queue check')
        # if the after timer is too short it might make the thing segfault
        self.after(10, self.check_queue)
        
    def crop_by_pzt(self,dc,pzt_lims):            
        mask = (dc['pzt'] > pzt_lims[0]) & (dc['pzt'] < pzt_lims[1])         
        dc2 = {}
        for key in dc:
            dc2[key] = dc[key][mask]        
        return dc2
        
    def kill_by_grad(self,t,pzt):
        kill_time = self.kill_time
        dt = t[1]-t[0] # seconds/samples
        kill_samples = int(np.round(kill_time/dt)) # samples
        # kill_samples = 10000
        pzt_grad = np.gradient(pzt)/dt
        good_ind = []
        
        if kill_samples == 0:
            # all indices are good
            good_ind = list(range(len(pzt)))
        else:
            # build a list of good ind by jumping by kill_samples if gradient is too negative
            jj = 0
            for i in range(len(pzt)):
                if jj > len(pzt)-1:
                    break
                # print(jj)
                grad = pzt_grad[jj]
                if grad > -1*100:
                    good_ind.append(jj)
                    jj += 1
                else:
                    jj += kill_samples
        
       # if good_ind[-1] >= len(pzt):
        #    print('!')
         #   print('!')
        #print(good_ind[-1],len(pzt))
        return good_ind
        
    def pull_channels_loop(self):
        while True:
                
            duration = self.duration
            
            # server might not always give data
            try:
                if self.omc_chan.t2 is None:
                    # let channel sort out what time to use
                    omc = self.omc_chan.getdata(duration)
                else:
                    omc = self.omc_chan.getdata(duration,t2=self.omc_chan.t2)
                    
                # subtract off dark floor
                omc -= self.dark_level
                    
                # synchronize pzt_chan to omc_chan
                pzt = self.pzt_chan.getdata(duration,t2=self.omc_chan.t2)
                
                # update omc_chan to next step
                self.omc_chan.t2 += self.advance_step
            except RuntimeError:
                print('RuntimeError. Likely empty data.')
                time.sleep(0.5)
                continue               
            except Exception as e:
                # skip iteration and try again later
                # usually it's because the connection breaks
                # probably need to reaquire the channels
                # have welcomescreen pass the channel mode and a channel_aquire 
                # method to mainapp so that we can restablish the connection at runtime
                print('Unexpected error caught at getdata. Reastablishing nds connection')
                print(e)
                #time.sleep(self.draw_speed)
                continue
            
            try:
                # in python2 every datatype is greater than None, so test for it explicitely
                if (self.omc_chan.t_end is not None) and (self.omc_chan.t2 > self.omc_chan.t_end):
                    print('successfully reached end of recording')
                    self.parent.destroy()
            except Exception:
                pass
                
           # if (self.ti is None) or ((self.omc_chan.t2 - self.ti) >= self.duration):
           #     self.recording = True
           #     self.ti = self.omc_chan.t2
                
            #print(self.ti,self.omc_chan.t2,(self.omc_chan.t2 - self.ti))
            
            #print('pre-resampling lengths ',len(omc),len(pzt)) 
            if len(omc) != len(pzt):
                #print('resampling')
                pzt = np.interp(np.linspace(0,1,len(omc)),np.linspace(0,1,len(pzt)),pzt)
            
            # check synchronicity
            #print(self.omc_chan.t1,self.omc_chan.t2)
            #print(self.pzt_chan.t1,self.pzt_chan.t2)
            
            t_start = self.omc_chan.t1
            
            t_end = t_start + duration
            t_vec = np.linspace(t_start,t_end,len(omc))
            #t_start = t_end
            
            #print('post resampling lengths: ',len(omc),len(pzt))
            
            mydecimate = lambda x,q: x[::q]
            
            t_vec = mydecimate(t_vec,self.q)
            omc = mydecimate(omc,self.q)
            pzt = mydecimate(pzt,self.q)
            
            # print('at grad kill')
            # print(len(t_vec),len(pzt))
            
            if self.rb_pzt_filter.var.get() == 'filter':
                good_ind = self.kill_by_grad(t_vec,pzt)
                #print(good_ind[-1],len(t_vec),len(pzt))
                
                t_vec = t_vec[good_ind]
                omc = omc[good_ind]
                pzt = pzt[good_ind]
            
            if len(t_vec) < 2:
                # if the block is less than 2 samples then just skip the entire block
                continue
            
            dt = t_vec[1]- t_vec[0]
            
            # print('at filt', len(omc),len(pzt))

            sort_ind = np.argsort(pzt)
            pzt_sort = pzt[sort_ind]
            omc_sort = omc[sort_ind]
            t_sort = t_vec[sort_ind]
            
            # print('at lowpass')
            
            if self.lowpass:
                omc_filt = brick_lowpass(omc,10,M=50,wn_fun=hann_wn)
            else:
                omc_filt = omc
            omc_filt_sort = omc_filt[sort_ind]

            # data needs to be packaged this way for OMC_scan lib
            dc = {}
            dc['omc'] = omc_filt_sort
            dc['pzt'] = pzt_sort
            dc['time'] = t_sort
                
            dc00 = self.crop_by_pzt(dc,self.zeroth.x)
            dc01 = self.crop_by_pzt(dc,self.first.x)
            dc02 = self.crop_by_pzt(dc,self.second.x)
                 
            # find location of peak in search bounds
            try:
                pidx_00 = np.argmax(dc00['omc'])
                a_00 = dc00['omc'][pidx_00]
                t_00 = dc00['time'][pidx_00]                 
                self.zeroth.mid = dc00['pzt'][pidx_00]
                self.zeroth.width = abs(self.zeroth.x[1] - self.zeroth.x[0])
                self.zeroth.x = np.array([-1,1])*self.zeroth.width/2 + self.zeroth.mid
                #print(self.zeroth.mid,self.zeroth.width )                   
            except Exception:
                pass
            
            try:
                pidx_01 = np.argmax(dc01['omc'])
                a_01 = dc01['omc'][pidx_01]
                t_01 = dc01['time'][pidx_01]
                self.first.mid = dc01['pzt'][pidx_01]
                self.first.width = abs(self.first.x[1] - self.first.x[0])
                self.first.x = np.array([-1,1])*self.first.width/2 + self.first.mid
            except Exception:
                pass
                
            try:
                pidx_02 = np.argmax(dc02['omc'])
                a_02 = dc02['omc'][pidx_02]
                t_02 = dc02['time'][pidx_02]
                self.second.mid = dc02['pzt'][pidx_02]
                self.second.width = abs(self.second.x[1] - self.second.x[0])
                self.second.x = np.array([-1,1])*self.second.width/2 + self.second.mid
                
                if len(self.t_mismatches) ==0 or (t_02 - self.t_mismatches[-1]) > 0.9*self.duration:
                    self.recording = True
            except Exception:
                pass
                                  
            if self.recording:
                self.recording = False
                
                print(a_00,a_02,a_02/a_00)
                print('recording at: ', dc02['time'][pidx_02])
                
                self.a00s.append([a_00,t_00])
                self.a02s.append([a_02,t_02])
                self.mismatches.append(a_02/a_00)
                self.t_mismatches.append(t_02)
                
                try:   
                    self.a01s.append([a_01,t_01])
                    self.misalignments.append(a_01/a_00)
                    self.t_misalignments.append(t_01)
                except Exception:
                    pass
                
            if self.rb_axscale.var.get() == 'semilogy':
                self.graph0.ax2.set_yscale('log')
                self.graph1.ax1.set_yscale('log')
                self.graph00.ax.set_yscale('log')
                self.graph01.ax.set_yscale('log')
                self.graph02.ax.set_yscale('log')
            else:
                self.graph0.ax2.set_yscale('linear')
                self.graph1.ax1.set_yscale('linear')
                self.graph00.ax.set_yscale('linear')
                self.graph01.ax.set_yscale('linear')
                self.graph02.ax.set_yscale('linear')
                
            self.graph0.line1.set_data(t_vec,pzt)
            self.graph0.line1.set_linestyle('')
            self.graph0.line1.set_marker('.')
            self.graph0.line1.set_ms(1)
            self.graph0.ax1.set_xlim(min(t_vec),max(t_vec))
            self.graph0.ax1.set_ylim(self.pzt_lim)
            self.graph0.ax1.grid(True)
            
            self.graph0.line2.set_data(t_vec,omc)
            self.graph0.line2.set_linestyle('')
            self.graph0.line2.set_marker('.')
            self.graph0.line2.set_ms(1)            
            # self.graph0.line3.set_color('red')
            self.graph0.ax2.set_xlim(min(t_vec),max(t_vec))
            self.graph0.ax2.set_ylim(self.omc_lim)
            self.graph0.ax2.grid(True)
            
            if self.xlim_opts.rb_mode.var.get() == 'automatic':
                self.graph0.ax1.relim()
                self.graph0.ax1.autoscale(enable=True, axis = 'y') 
                
            if self.ylim_opts.rb_mode.var.get() == 'automatic':    
                self.graph0.ax2.relim()
                self.graph0.ax2.autoscale(enable=True, axis = 'y')
                
            self.graph0.canvas.draw()
            
            self.graph1.line1.set_data(dc['pzt'],dc['omc'])
            self.graph1.ax1.grid(True)
            self.graph1.ax2.grid(True)
            
            if self.xlim_opts.rb_mode.var.get() == 'automatic':
                self.graph1.ax1.relim()
                self.graph1.ax1.autoscale(enable=True, axis = 'x') 
            else:    
                self.graph1.ax1.set_xlim(self.pzt_lim)
                
            if self.ylim_opts.rb_mode.var.get() == 'automatic':
                self.graph1.ax1.relim()
                self.graph1.ax1.autoscale(enable=True, axis = 'y')
            else:
                self.graph1.ax1.set_ylim(self.omc_lim)
            
            self.graph1.line2.set_data(self.t_mismatches[-self.m_range:],self.mismatches[-self.m_range:])
            self.graph1.line3.set_data(self.t_misalignments[-self.m_range:],self.misalignments[-self.m_range:])
            self.graph1.ax2.relim()
            self.graph1.ax2.autoscale()
            
            self.graph1.canvas.draw()

            self.graph00.line.set_data(dc00['pzt'],dc00['omc'])
            try:
                self.graph00.line2.set_data(dc00['pzt'][np.argmax(dc00['omc'])],np.max(dc00['omc']))
            except Exception:
                pass
            self.graph00.line2.set_ls('')
            self.graph00.line2.set_marker('x')
            self.graph00.line2.set_color('r')
            self.graph00.line2.set_mew(2.0)
            self.graph00.line2.set_ms(10.0)
            self.graph00.ax.relim()
            self.graph00.ax.autoscale()  
            self.graph00.ax.grid(True)   
            
            self.graph01.line.set_data(dc01['pzt'],dc01['omc'])
            try:
                self.graph01.line2.set_data(dc01['pzt'][np.argmax(dc01['omc'])],np.max(dc01['omc']))
            except Exception:
                pass
            self.graph01.line2.set_ls('')
            self.graph01.line2.set_marker('x')
            self.graph01.line2.set_color('r')
            self.graph01.line2.set_mew(2.0)
            self.graph01.line2.set_ms(10.0)
            self.graph01.ax.relim()
            self.graph01.ax.autoscale()
            self.graph01.ax.grid(True)  
            
            self.graph02.line.set_data(dc02['pzt'],dc02['omc'])
            try:
                self.graph02.line2.set_data(dc02['pzt'][np.argmax(dc02['omc'])],np.max(dc02['omc']))
            except Exception:
                pass
            self.graph02.line2.set_ls('')
            self.graph02.line2.set_marker('x')
            self.graph02.line2.set_color('r')
            self.graph02.line2.set_mew(2.0)
            self.graph02.line2.set_ms(10.0)
            self.graph02.ax.relim()
            self.graph02.ax.autoscale()
            self.graph02.ax.grid(True)
                
            self.graph00.canvas.draw()
            self.graph01.canvas.draw()
            self.graph02.canvas.draw()
            
            #time.sleep(self.draw_speed)
