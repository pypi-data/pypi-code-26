try:
    import nds2
except:
    pass

from subprocess import check_output

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
    def __init__(self,nds_server,channel_name,t1,rec_time):
        self.t1 = t1
        self.t2 = None
        self.t_start = t1
        self.rec_time = rec_time
        self.t_end = t1 + rec_time
        self.s1 = 0
        self.channel_name = channel_name
        
        # initialize nds connection
        self.nds_chan = nds2.connection(nds_server,8088)
        
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
    def __init__(self,nds_server,channel_name):
        self.channel_name = channel_name
        self.nds_chan = None
        self.t_start = self.t_now()
        self.t_end = None
        self.t1 = None
        self.t2 = None
        self.nds_offset = 1 # how many seconds behind nds we have to be
        # not really sure how this works
        self.nds_chan = nds2.connection(nds_server,8088) # initialize nds connection
        
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
        #print(self.t1,self.t2)
        return self.nds_chan_buff.data
