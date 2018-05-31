__version__ = "0.2.3"

import numpy as np
import sys
import os
#from PIL import ImageTk, Image
if __name__ == '__main__':
    module_path = '.'
else:
    #print(sys.modules[__name__]).__file__
    module_path = os.path.dirname(sys.modules[__name__].__file__)
    #print(module_path)

from subprocess import check_output
if sys.version_info[0] < 3:
    import Tkinter as tk
    from exceptions import Exception
else:
    import tkinter as tk
    
from main_frame import MainApplication
from tk_frames import RadioOption, OptionsParser, enable, disable
from channels import *

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

class WelcomeScreen(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.omc_channel_name = IFO + ':OMC-DCPD_SUM_OUT_DQ'
        self.pzt_channel_name = IFO + ':OMC-PZT2_EXC'
        self.pzt_historic_channel_name = IFO + ':OMC-PZT2_MON_DC_OUT_DQ'
        self.nds_server = IFO + 'nds1'
        
        self.t1 = None
        self.t2 = None
        self.duration = None
        
        if any([True for x in ['--verbose','-v'] if x in sys.argv]):
            self.verbose = True
        else:
            self.verbose = False
       
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
        #self.img = Image.open("uofa_logo.png")
        #aspect_ratio = self.img.size[0]/float(self.img.size[1])
        #self.img = self.img.resize((int(250*aspect_ratio), 250), Image.ANTIALIAS)
        self.img = tk.PhotoImage(file=module_path + '/uofa_logo_250.png')
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
            omc_chan = historic_channel_continuous(self.nds_server,self.omc_channel_name,self.t1,self.rec_time)
            print('omc loaded')
            pzt_chan = historic_channel_continuous(self.nds_server,self.pzt_historic_channel_name,self.t1,self.rec_time)
            print('pzt loaded')
            
        elif mode == 'realtime':           
            omc_chan = realtime_channel(self.nds_server,self.omc_channel_name)
            pzt_chan = realtime_channel(self.nds_server,self.pzt_channel_name)
            print('Not yet fully tested')
            
            
        # clear frame
        self.destroy()
        # insert mainapp frame
        mainapp = MainApplication(self.parent,omc_chan,pzt_chan)
        mainapp.verbose = self.verbose
        mainapp.mode = mode
        mainapp.omc_channel_name = self.omc_channel_name
        mainapp.pzt_channel_name = self.pzt_channel_name
        mainapp.pzt_historic_channel_name = self.pzt_historic_channel_name
        mainapp.nds_server = self.nds_server
        mainapp.acquire_channels = lambda: [realtime_channel(self.pzt_channel_name)
        ,realtime_channel(self.omc_channel_name)]
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
