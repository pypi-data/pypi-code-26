import matplotlib as mpl
mpl.use("TkAgg") # needs to be there
from matplotlib.backends import backend_tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import sys
if sys.version_info[0] < 3:
    import Tkinter as tk
    from exceptions import *
else:
    import tkinter as tk

def disable(tk_obj):
    try:
        tk_obj.configure(state=tk.DISABLED)
    except Exception:
        pass
    for child in tk_obj.winfo_children():
        try:
            disable(child)
        except Exception:
            pass
            
def enable(tk_obj):
    try:
        tk_obj.configure(state=tk.NORMAL)
    except Exception:
        pass
    for child in tk_obj.winfo_children():
        try:
            enable(child)
        except Exception:
            pass

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
        self.text = tk.Text(self.win0,wrap=tk.WORD)
        self.text.pack(side='top',fill='both',expand=True)
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
               
        self.rb_mode = RadioOption(self._group2,['automatic','manual'],default='automatic',command=self.onchange)
        self.rb_mode.pack(side='top')
        
        self.title_label.pack(anchor='w')
        self._group2.pack(anchor='w')
        self._group1.pack(anchor='w')
        
    def submit(self):
        self.target[0] = float(self.min_entry.get())
        self.target[1] = float(self.max_entry.get())
        
    def onchange(self):
        if self.rb_mode.var.get() == 'automatic':
            disable(self._group1)
        else:
            enable(self._group1)
        
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
