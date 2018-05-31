#
#-*- coding:utf-8 -*-
"""
A module to support Tektronix TDS3000 series OSC. Mostly work with other OSC from Tektronix, with minor modification.
(C) Noboru Yamamoto,2009. KEK, Ibaraki, JAPAN

Referenc:
 "TDS3000,TDS3000B, and TDS3000C series Digital Phosphor Oscilloscopes", 071--381-03,Tektronix

 RPC server info on TDS300
  Get RPC info
   program vers proto   port
    395183    1   tcp   1008
    395184    1   tcp   1005
"""
#
# data objects
#
class Tekwaveform:
    enc={"ASCII":"%d","RIBINARY":">h",'RPBINARY':">H",'SRIBINARY':"<h",'SRPBINARY':"<H"}
    BFMT={'RI':"h",'RP':"H"}
    BORD={"MSB":">","LSB":"<"}
    def __init__(self,data):
        self.rdata=data.split(";")
        if (len(self.rdata) < 17):
            sys.stderr.write(self.rdata[:16],len(self.rdata))
            raise ValueError("Not enough data")
        wfdata=";".join(self.rdata[16:])

        self.byte_width=int(self.rdata[0])
        self.bit_width=int(self.rdata[1])
        self.ENC=self.rdata[2]
        self.BIN_FMT=self.rdata[3]
        self.BYTE_ORDER=self.rdata[4]
        self.Data_Num=int(self.rdata[5])
        self.wfid=self.rdata[6]
        self.point_fmt=self.rdata[7]
        self.X_Incr=float(self.rdata[8])
        self.Point_Offset=int(self.rdata[9])
        self.X_Zero=float(self.rdata[10])
        self.X_Unit=self.rdata[11]
        self.Y_Mult=float(self.rdata[12])
        self.Y_Zero=float(self.rdata[13])
        self.Y_Offset=float(self.rdata[14])
        self.Y_Unit=self.rdata[15]
        self.TS=None
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.conv_fmt=float
            self.wfsize=""
            if (wfdata[0] == ":"):
                self.raw=wfdata[len(":CURVE "):-1]
            else:
                self.raw=wfdata[:-1]
        else:
            self.conv_fmt=self.BORD[self.BYTE_ORDER]+self.BFMT[self.BIN_FMT]
            if (wfdata[0] == "#"):
                sz=2+int(wfdata[1])
                self.wfsize=dsz=int(wfdata[2:sz])
                print "data size:",dsz
                self.raw=wfdata[sz:-1]
            else:
                self.raw=wfdata[:-1]
        self._convert()
        
    def update(self,curve):
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.wfsize=""
            if (curve[0] == ":"):
                self.raw=curve[len(":CURVE "):-1]
            else:
                self.raw=curve[:-1]
        else:
            if (curve[0] == "#"):
                sz=2+int(curve[1])
                self.wfsize=dsz=int(curve[2:sz])
                self.raw=curve[sz:-1]
            else:
                self.raw=curve[:-1]
        self._convert()

    def _convert(self):
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.wf=[float(x) for x in self.raw.split(",")]
        else:# binary
            # consider to use scipy.fromstring if scipy is avaialble
            #if _use_numpy_fromstring:
            #self.wf=numpy.fromstring(self.raw[i:i+self.byte_width],dtype=np.uint,count=len(self.raw)/self.byte_width,sep='')
            #else
            self.wf=[struct.unpack(self.conv_fmt,
                                   self.raw[i:i+self.byte_width])[0]
                     for i in range(0,len(self.raw),self.byte_width)]

        self.y=[((y-self.Y_Offset)*self.Y_Mult+self.Y_Zero) for y in self.wf]
        self.x=[ (x*self.X_Incr+self.X_Zero) for x in range(len(self.y))]
        
    def trace(self):
        return zip(self.x,self.y)

#
# data objects
#
class DPOwaveform(Tekwaveform):
    enc={"ASCII":"%d","RIBINARY":">h",'RPBINARY':">H",'SRIBINARY':"<h",'SRPBINARY':"<H"}
    BFMT={'RI':{1:"b",2:"h",4:"l",8:"q"},'RP':{1:"B",2:"H",4:"L",8:"Q"}}
    BORD={"MSB":">","LSB":"<"}
    """
    Preample for TDS3k:
        
    preamble for DPO3k:
    >>> dpo3k.ask(":WFMO?;")
    '1;8;BIN;RI;MSB;"Ch1, DC coupling, 5.000mV/div, 400.0us/div, 10000 points, Sample mode";10000;Y;"s";400.0000E-9;-2.0000E-3;0;"V";200.0000E-6;0.0E+0;0.0E+0\n'

    preamble for DPO7k:
    >>> dpo7k.ask(":WFMO?;")
    '2;16;BIN;RI;MSB;"Ch1, DC coupling, 1.000mV/div, 1.000us/div, 10000 points, Sample mode";10000;Y;"s";1.0000E-9;0.0000;5000;"V";156.2500E-9;18.4320E+3;0.0000;1\n'
    """

    def __init__(self,preamble,wfdata):
        """
        Examples WAVFRM? might return the waveform data as:(VERBOSE 0, header 1)
        :WFMOUTPRE:BYT_NR 1;BIT_NR 8;ENCDG ASCII;BN_FMT RI;BYT_OR MSB;
        "Ch1, DC coupling, 100.0mV/div, 4.000us/div, 10000 points, Sample ";
        NR_PT 20;PT_FMT Y;X_UNIT "s";XINCR 4.0000E-9;XZERO -20.0000E-6;PT_OFF 0;
        YUNIT "V";YMULT 4.0000E-3;YOFF 0.0000;YZERO 0.0000;
        :CURVE 2,1,4,2,4,3,0,3,3,3,3,3,3,4,3,5,6,6,7,3....
        """
        self.rdata=preamble.split(";")
        self.rdata.append(wfdata)
        if (len(self.rdata) < 17):
            sys.stderr.write("%s data read:"%(self.rdata[:16], len(self.rdata)))
            raise ValueError("Not enough data")

        self.byte_width=int(self.rdata[0])
        self.bit_width=int(self.rdata[1])
        self.ENC=self.rdata[2]
        self.BIN_FMT=self.rdata[3]
        self.BYTE_ORDER=self.rdata[4]
        self.wfid=self.rdata[5]
        self.Data_Num=int(self.rdata[6])
        self.point_fmt=self.rdata[7]
        self.X_Unit=self.rdata[8]
        self.X_Incr=float(self.rdata[9])
        self.X_Zero=float(self.rdata[10])
        self.Point_Offset=int(self.rdata[11])
        self.Y_Unit=self.rdata[12]
        self.Y_Mult=float(self.rdata[13])
        self.Y_Offset=float(self.rdata[14])
        self.Y_Zero=float(self.rdata[15])

        # curve start from rdata[16]
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.conv_fmt=float
            self.wfsize=""
            if (curve[0] == ":"):# ? where is curve definition?
                self.raw=wfdata[len(":CURVE "):-1]
            else:
                self.raw=wfdata[:-1]
        else:
            self.conv_fmt=self.BORD[self.BYTE_ORDER]+self.BFMT[self.BIN_FMT][self.byte_width]
            if (wfdata[0] == "#"):
                sz=2+int(wfdata[1])
                self.wfsize=dsz=int(wfdata[2:sz])
                self.raw=wfdata[sz:-1]
            else:
                self.raw=wfdata[:-1]
        #
        self._convert()

    def _convert(self):
        if (self.ENC == "ASCII" or self.ENC == "ASC"):
            self.wf=[float(x) for x in self.raw.split(",")]
        else:
            self.wf=[struct.unpack(self.conv_fmt,
                                   self.raw[i:i+self.byte_width])[0]
                     for i in range(0,len(self.raw),self.byte_width)]
        
        self.y=[((y-self.Y_Offset)*self.Y_Mult+self.Y_Zero) for y in self.wf]
        self.x=[ (x*self.X_Incr+self.X_Zero) for x in range(len(self.y))]
    

if __name__ == "__main__":
    test()
