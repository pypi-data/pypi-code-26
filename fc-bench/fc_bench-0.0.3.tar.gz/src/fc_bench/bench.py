# Copyright (C) 2018 F. Cuvelier
from __future__ import print_function
import numpy as np

def gitinfo():
  return {'name': 'fc-bench', 'tag': '0.0.3', 'commit': '6fabbfb9ab5d08281670bb13131980bdecb58012', 'date': '2018-05-18', 'time': '12-55-12', 'status': '0'} # automatically updated
  if len(inf)>0: # Only for developpers
    return inf
  import fc_tools,fc_bench,os
  D=os.path.realpath(os.path.join(fc_bench.__path__[0],os.path.pardir))
  if os.path.basename(D)=='src':
    D=os.path.realpath(os.path.join(D,os.path.pardir))
  return fc_tools.git.get_info(D)
    

class bData:
  def __init__(self,name,value,sformat,strlen=0):
    self.name=name # str
    self.value=value # scalar
    self.sformat=sformat # example '{:8}' for integer, '{:8.3f}' '{:12.3e}'   for double, '{:>10}' for string
    self.strlen=0
    self.numpy=''
    self.strnumpy()
    self.set_strlen(strlen)
    
  def str(self):
    return self.sformat.format(self.value)
  
  def strnumpy(self):
    #print(type(self.value))
    if isinstance(self.value,int) or np.issubdtype(type(self.value),np.integer):
      self.numpy='i4'
      return
    
    if isinstance(self.value,float) or np.issubdtype(type(self.value),np.float):
      self.numpy='f4'
      return  
    
  def set_strlen(self,slen):
    self.strlen=max(len(self.name),len(self.sformat),len(self.sformat.format(self.value)),slen)+2

def setfun(N,verbose,**kwargs):
  import fc_oogmsh,fc_mesh
  d=kwargs.pop('d',2) # in [2,2.5,3]
  Type=kwargs.pop('Type',None) # Type of simplices 1: Lines, 2: Triangles, 4: Tedrahedra 
  geofile=kwargs.pop('geofile','condenser11')
  meshfile=fc_oogmsh.buildmesh(d,geofile,N,verbose=0,**kwargs)
  oGh=fc_oogmsh.ooGmsh(meshfile)
  
  if Type is None:
    Type=2 # Triangles
    if oGh.dim==3 and (4 in oGh.types):
      Type=4
  assert Type in oGh.types
  q,me=oGh.extractElement(Type)
  dim,d,nq,nme=fc_mesh.simplicial.get_dims(q,me)
  if verbose:
    print('# geofile: %s'%geofile)
    print('#  -> dim=%d, d=%d'%(dim,d))
  
  bDs=[bData('{:>8}'.format('N'),N,'{:8}'),bData('{:>8}'.format('nq'),nq,'{:8}'),bData('{:>8}'.format('nme'),nme,'{:8}')]
  return ((q,me),bDs)

def line_text_delimiter():
  return '#'+ 75*'-'

def str_bDs(bDs):
  #s=' '*8 # len of '#labels:'
  s=''
  for bD in bDs:
    sf='{:>%d}'%bD.strlen
    s+=sf.format(bD.str())
  return s

def formats_bDs(bDs):
  s='#format:' 
  for bD in bDs:
    #l=len(bD.name)
    l=bD.strlen
    fmt='{:>%d}'%l
    s+=fmt.format(bD.sformat)
  return s

def numpy_bDs(bDs):
  s='#numpy: ' 
  for bD in bDs:
    #l=len(bD.name)
    l=bD.strlen
    fmt='{:>%d}'%l
    s+=fmt.format(bD.numpy)
  return s

def title_bDs(bDs):
  s=''
  for bD in bDs:
    sf='{:>%d}'%bD.strlen
    s+=sf.format(bD.name)
  st='#labels:'  
  s=st+s
  return s,len(st)

def print_info(**kwargs):
  Print=kwargs.pop('Print',lambda s: print(s))
  import fc_tools.Sys as fc_sys 
  CPU=fc_sys.getCPUinfo();
  OS=fc_sys.getOSinfo();
  Print('#%12s: %s'%('computer',fc_sys.getComputerName()))
  Print('#%12s: %s (%s)'%('system',OS['description'],OS['arch']))
  Print('#%12s: %s'%('processor',CPU['name']))
  Print('#%13s (%d procs/%d cores by proc/%d threads by core)'%(' ',CPU['nprocs'],CPU['ncoreperproc'],CPU['nthreadspercore']))
  Print('#%12s: %3.1f Go'%('RAM',fc_sys.getRAM()))
  soft,release=fc_sys.getSoftware()
  Print('#%12s: %s'%('software',soft))
  Print('#%12s: %s'%('release',release))


def mean_run(fun,datas,nbruns,copyinput):
  import time
  import numpy as np
  Tcpu=np.zeros((nbruns+2,))
  if copyinput: # if input is modified
    import copy
    datascopy=copy.deepcopy(datas)
  else:
    datascopy=datas
    
  for i in range(0,nbruns+2):
    if isinstance(datas,tuple):
      tstart=time.time()
      Out=fun(*datascopy)
      Tcpu[i]=time.time()-tstart
    else:
      tstart=time.time()
      Out=fun(datascopy)
      Tcpu[i]=time.time()-tstart
    if copyinput:
      #Out=copy.deepcopy(Out)
      datascopy=copy.deepcopy(datas)
  Tcpu.sort()  
  tcpu=np.mean(Tcpu[1:-1])
  return tcpu,Out

def biprint(S,fid):
  print(S)
  if fid is not None:
    fid.write(S+'\n')
    
def funname_small(fun):
  if isinstance(fun,str):
    name=fun
  else:
    name=fun.__name__
  I=name.rfind('.')
  if I>=0:
    name=name[I+1:]
  I=name.rfind('_')
  if I>=0:
    name=name[:I]
  return name  

def build_open_filename(Fun,**kwargs):
  name=kwargs.pop('name','')
  tag=kwargs.pop('tag','')
  Date=kwargs.pop('date',False)
  savefile=kwargs.pop('savefile', '')
  save=kwargs.pop('save',False)
  savedir=kwargs.pop('savedir', '') # relative to currrent path. default 'benchs'
  import time,os
  from fc_tools.others import mkdir_p
  DateNum=time.time()
  fid=None
  if len(savefile)>0 or len(savedir)>0 or len(tag)>0:
    save=True    
  if not save:  
    return (fid,savefile,DateNum)
  if len(savedir)==0:
    savedir='benchs'
  mkdir_p(savedir)  
  
  if len(savefile)==0:
    savefile=funname_small(Fun)
  savefile, ext = os.path.splitext(savefile)
  if len(ext)==0:
    ext='.out'
  if Date:
    strdate=time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(DateNum))
  else:
    strdate=''
  if len(tag)>0:  
    savefile+='_'+tag
  if len(strdate)>0:  
    savefile+='_'+strdate
  savefile=os.path.join(savedir,savefile+ext)
  try:
    fid=open(savefile,'w')
  except IOError:
    print("Could not open file <%s> !"%savefile)
  return (fid,savefile,DateNum)
      
def strfun(fun):
  from fc_tools.others import is_lambda_function,func2str
  if is_lambda_function(fun):
    return func2str(fun,source=True)
  else:
    return func2str(fun,source=False)

def bench(Lfun,setfun,**kwargs):
  import time
  #from inspect import getfullargspec
  from fc_tools.others import is_function,get_nargin
  LN=kwargs.pop('LN', [5,10,15])
  #LN=np.array(LN,dtype=int)
  nbruns=kwargs.get('nbruns', 5)
  debug=kwargs.pop('debug', True)
  Error=kwargs.pop('error', None)
  comment=kwargs.pop('comment', [])
  info=kwargs.pop('info', True)
  copyinput=kwargs.pop('copyinput', False) 
  labelsinfo=kwargs.pop('labelsinfo', False)
  names=kwargs.pop('names', None)
  if names is None:
    names=[]
    for fun in Lfun:
      names.append(fun.__name__)
  else:
    assert len(names)==len(Lfun)
    for i in range(len(names)):
      if len(names[i])==0:
        names[i]=Lfun[i].__name__
  
  if isinstance(comment,str):
    comment=[comment]
      
  (fid,savefile,DateNum)=build_open_filename(names[0],**kwargs)    
  Print=lambda S: biprint(S,fid)  
  
  ltd=line_text_delimiter()
  biprint(ltd,fid)
  if info:
    print_info(Print=Print)
    biprint(ltd,fid)
  if len(comment)!=0:
    for i in range(len(comment)):
      Print(comment[i])
    biprint(ltd,fid)  
  if labelsinfo:
    Print('# Benchmarking functions:')
    for i in range(len(names)):
      Print('#  fun[%d], %14s: %s'%(i,names[i],strfun(Lfun[i])))
    if Error is not None:
      Print('# cmpErr[i], error between fun[0] and fun[i] outputs computed with function')
      Print('#    %s'%strfun(Error))
      Print('# where')
      Print('#    - 1st input parameter is the output of fun[0]')
      Print('#    - 2nd input parameter is the output of fun[i]')
    Print(ltd)  
    
  datas,bDs=setfun(LN[1],True,Print=Print,**kwargs)
  biprint(ltd,fid)
  nfun=len(Lfun)
  isTitle=False

  for N in LN:
    datas,bDs=setfun(N,False,**kwargs);
    if is_function(datas[-1]):
      funerror=datas[-1]
      datas=datas[:-1]
    else:
      funerror=None
    fun=Lfun[0]
    tcpu,OutRef=mean_run(fun,datas,nbruns,copyinput)
    name='  '+names[0]+'(s)'
    bDs.append(bData(name,tcpu,'{:%d.3f}'%(len(name))))
    if funerror is not None:
      if get_nargin(funerror)==len(OutRef):
        E=funerror(*OutRef)
      else:
        E=funerror(OutRef)
      name='  '+'Error[0]'
      bDs.append(bData(name,E,'{:%d.3e}'%(len(name))))
    for k in range(1,nfun):
      fun=Lfun[k]
      tcpu,Out=mean_run(fun,datas,nbruns,copyinput)
      name='  '+names[k]+'(s)'
      bDs.append(bData(name,tcpu,'{:%d.3f}'%(len(name))))
      if funerror is not None:
        if get_nargin(funerror)==len(OutRef):
          E=funerror(*OutRef)
        else:
          E=funerror(OutRef)
        name='  '+'Error[%d]'%k
        bDs.append(bData(name,E,'{:%d.3e}'%(len(name))))
      if Error is not None:
        E=Error(OutRef,Out)
        name='  '+'cmpErr[{}]'.format(k)
        bDs.append(bData(name,E,'{:%d.3e}'%(len(name))))
    if not isTitle:
      if len(savefile)>0:
        Print('#benchfile: %s'%savefile)
      Print('#date:{}'.format(time.strftime('%Y/%m/%d %H:%M:%S')))
      Print('#nbruns:{}'.format(nbruns))
      #biprint('#date: '+time.ctime(DateNum),fid)
      biprint(numpy_bDs(bDs),fid)
      biprint(formats_bDs(bDs),fid)
      slabels,ns=title_bDs(bDs)
      biprint(slabels,fid)
      isTitle=True
    biprint(' '*ns+str_bDs(bDs),fid)
  
  if fid is not None:
    fid.close()
