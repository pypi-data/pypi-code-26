__version__ = "0.1.6"

import numpy as np
import sys
import os
from PIL import ImageTk, Image

from subprocess import check_output
if sys.version_info[0] < 3:
    import Tkinter as tk
    from exceptions import Exception
else:
    import tkinter as tk
    
from main_frame import MainApplication, RadioOption, OptionsParser, enable, disable

try:
    import nds2
except:
    pass

# IFO == H1 -> Hanford
# IFO == L1 -> Livingston
try:
    IFO = os.environ['IFO']
except Exception:
    print('IFO environment variable not defined. Assuming H1')
    IFO = 'H1'

class old_historic_channel:
    
    def __init__(self,data_vec,Fs,t1,t2):
        self.data = data_vec
        self.Fs = Fs
        self.t1 = t1
        self.t2 = None
        self.tend = t2
        self.time = 1208580738
        n = 200
        self.s1 = n*Fs # offset first point
    
    def getdata(self,duration,t_pull=1,t2=None):
        self.s2 = self.s1 + self.Fs*duration
        grab = self.data[self.s1:self.s2]
        self.s1 += t_pull*self.Fs
        self.t1 += t_pull
        self.t2 = self.t1 + duration
        return grab
        
# This one should never be used
class historic_channel(old_historic_channel):
    def __init__(self,channel_name,t1,duration):
        self.t1 = t1
        self.duration = duration
        self.t2 = t1 + duration
        self.s1 = 0
        self.channel_name = channel_name
        
        # initialize nds connection
        self.nds_chan = nds2.connection(IFO+'nds1',8088)
        # fetch entire data block
        self.nds_buff = self.nds_chan.fetch(self.t1,self.t2,[self.channel_name])
        self.Fs = int(self.nds_buff[0].sample_rate)
        self.data = self.nds_buff[0].data      
        
class historic_channel_continuous:
    def __init__(self,channel_name,t1,rec_time):
        self.t1 = t1
        self.t2 = None
        self.t_start = t1
        self.rec_time = rec_time
        self.t_end = t1 + rec_time
        self.s1 = 0
        self.channel_name = channel_name
        
        # initialize nds connection
        self.nds_chan = nds2.connection(IFO+'nds1',8088)
        
    def getdata(self,duration,t2=None):
        self.duration = duration
        
        if t2 is not None:
            self.t2 = t2
            self.t1 = self.t2 - duration
        else:
            self.t2 = self.t1 + duration
            
        self.nds_chan_buff = self.nds_chan.fetch(self.t1,self.t2,[self.channel_name])[0]
        self.sample_rate = self.nds_chan_buff.sample_rate
        #print(self.t1,self.t2)
        return self.nds_chan_buff.data
        
class realtime_channel:
    def __init__(self,channel_name):
        self.channel_name = channel_name
        self.nds_chan = None
        self.t_start = self.t_now()
        self.t_end = None
        self.t1 = None
        self.t2 = None
        self.nds_offset = 1 # how many seconds behind nds we have to be
        # not really sure how this works
        self.nds_chan = nds2.connection('h1nds1',8088) # initialize nds connection
        
    def t_now(self):
        return int(check_output(['tconvert', 'now']))
        
    def getdata(self,duration,t2=None):
        ''' duration should be an integer '''
        if t2 == None:
            self.t2 = self.t_now() - self.nds_offset
        else:
            self.t2 = t2
        self.t1 = self.t2 - duration
        self.nds_chan_buff = self.nds_chan.fetch(self.t1,self.t2,[self.channel_name])[0]
        self.sample_rate = self.nds_chan_buff.sample_rate
        print(self.t1,self.t2)
        return self.nds_chan_buff.data

class WelcomeScreen(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.omc_channel_name = IFO + ':OMC-DCPD_SUM_OUT_DQ'
        #self.pzt_channel_name = 'H1:OMC-PZT2_OUT'
        self.pzt_channel_name = IFO + ':OMC-PZT2_EXC'
        #self.pzt_channel_name  = 'H1:OMC-PZT2_OUTPUT'
        self.pzt_historic_channel_name = IFO + ':OMC-PZT2_MON_DC_OUT_DQ'
        self.t1 = None
        self.t2 = None
        self.duration = None
       
        # t1=1208580738
        
        # t1=1210187830
        
        self.row1 = tk.Frame(self)
        self.col1 = tk.Frame(self.row1)
        self.col2 = tk.Frame(self.row1)
        
        self.duration_label = tk.Label(self.col1,text='duration=')
        self.duration_entry = tk.Entry(self.col2)
        self.duration_entry.insert(0, "20")
        self.duration_label.pack(side='top',anchor='e')
        self.duration_entry.pack(side='top')
        
        self.t1_label = tk.Label(self.col1,text='t1=')
        self.t1_entry = tk.Entry(self.col2)
        self.t1_entry.insert(0, "1210187830")
        self.t1_label.pack(side='top',anchor='e')
        self.t1_entry.pack(side='top')
        
        self.rec_time_label = tk.Label(self.col1,text='rec_time=')
        self.rec_time_entry = tk.Entry(self.col2)
        self.rec_time_entry.insert(0, "17500")
        self.rec_time_label.pack(side='top',anchor='e')
        self.rec_time_entry.pack(side='top')

        self.modes = ['old_historic (debugging)','historic','realtime']
        self.rb = RadioOption(self,self.modes,default=self.modes[1],command=self.on_rb_change)
        self.on_rb_change()
        self.startbutton = tk.Button(master=self, text='start', command=self.start)
        
        self.rb.pack(side='top',expand=True,anchor='n',pady=10)
        self.col1.pack(side='left')
        self.col2.pack(side='left')
        self.row1.pack(side='top',pady=10)
        self.startbutton.pack(side='top',expand=True,pady=10)
        
        # add uofa_logo
        self.img = Image.open("uofa_logo.png")
        aspect_ratio = self.img.size[0]/float(self.img.size[1])
        self.img = self.img.resize((int(250*aspect_ratio), 250), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(self.img)
        self.panel = tk.Label(self,image=self.img)
        self.panel.pack(pady=10)
        
    def on_rb_change(self):
        if self.rb.var.get() == self.modes[0]:
            # debug
            disable(self.col2)
        elif self.rb.var.get() == self.modes[1]:
            # historic
            enable(self.col2)
        elif self.rb.var.get() == self.modes[2]:
            # realtime
            disable(self.col2)
            enable(self.duration_entry)
        
    def acquire_channel(self,channel_name):
        pass
        
    def start(self):
    
        self.t1 = int(self.t1_entry.get())
        self.duration = int(self.duration_entry.get())
        self.rec_time = int(self.rec_time_entry.get())
        mode = self.rb.var.get()
        if mode == 'old_historic (debugging)':
            omc_data = np.load('../omc.npy')
            pzt_data = np.load('../pzt.npy')
            
            t1 = 1208580738
            t2 = 1208582718
            Fs = 2**14 # 16384 Hz
            
            time_channel = np.linspace(t1,t2,len(pzt_data))
            time_channel2 = np.linspace(t1,t2,len(omc_data))

            # pzt channel is downampled, reinterpolate
            pzt_data2 = np.interp(time_channel2,time_channel,pzt_data)

            omc_chan = old_historic_channel(omc_data,Fs,t1,t2)
            pzt_chan = old_historic_channel(pzt_data2,Fs,t1,t2)
            
        elif mode == 'historic':
            omc_chan = historic_channel_continuous(self.omc_channel_name,self.t1,self.rec_time)
            print('omc loaded')
            pzt_chan = historic_channel_continuous(self.pzt_historic_channel_name,self.t1,self.rec_time)
            print('pzt loaded')
            
        elif mode == 'realtime':           
            omc_chan = realtime_channel(self.omc_channel_name)
            pzt_chan = realtime_channel(self.pzt_channel_name)
            print('Not yet fully tested')
            
            
        # clear frame
        self.destroy()
        # insert mainapp frame
        mainapp = MainApplication(self.parent,omc_chan,pzt_chan)
        mainapp.duration = self.duration
        mainapp.pack(side="left", fill="both", expand=True)
        # resize window for new frame
        mainapp.parent.geometry("1200x620")
        mainapp.start()

def main():

    root = tk.Tk()
    root.title("OMC Scanalyzer")
    root.geometry("600x480")
    welcome = WelcomeScreen(root)
    welcome.pack(side='top',expand=True)
    
    # mainapp.pack(side="top", fill="both", expand=True)
    
    root.mainloop()
    
if __name__ == "__main__":
    main()
