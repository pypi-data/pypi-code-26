#! C:\Python27
from copy import deepcopy
# from inspect import getargspec
import time
import os

import numpy as np
import pandas as pd

from bd_resample import *
from reg_bd_svd import *
from reg_bd3 import *

def bdreg_v1(B,N=None,VamModel=None,BuildModel=None):
    np.set_printoptions(precision=5,suppress=True)

    if N == None:
        N=50

    if not BuildModel:
        print 'applying model'
        N = VamModel['N']
    elif BuildModel:
        print 'building model'
        VamModel['N']= N

    bduse=deepcopy(B)
    plotres=0
    bnreg=deepcopy(bduse)
    bnreg0=deepcopy(bnreg)
    kll=len(bduse)
    bdpc=np.zeros([kll,2*N])
    bdpc0=deepcopy(bdpc)
    sc=np.zeros([kll,1])
    for ktt in range(kll):
        bdt=bd_resample((bduse.loc[ktt]),N)
        bnreg0.loc[ktt],sc[ktt]=reg_bd_svd(bdt)
        bdpc0[ktt]=np.append([bnreg0[ktt][1]],[bnreg0[ktt][0]],axis=1)
    mbdpc0 = [sum(x)/len(x) for x in zip(*bdpc0)]
    bdr0=np.append([mbdpc0[N:]],[mbdpc0[0:N]],axis=0)

    if BuildModel:
        bdrn=deepcopy(bdr0)
        VamModel['bdrn']=bdrn
    else:
        bdrn=VamModel['bdrn']

    outyt=np.zeros([kll,1])
    bnreg=deepcopy(bnreg0)

    for tt0 in range(1):
        for ktt in range(kll):
            bnreg[ktt],outyt[ktt]=reg_bd3(bnreg.loc[ktt],bdrn)
            bdpc[ktt]=np.append(bnreg[ktt][1],bnreg[ktt][0])
            if plotres: #no plotting
                print(ytot)
                bdnew=bnreg.loc[ktt]
                figure(2)
                plot(bdnew[:,2],bdnew[:,1],'b-',bdr0[:,2],bdr0[:,1],'r-')
                hold('on')
                plot(bdnew[1,2],bdnew[1,1],'ro')
                plot(bdnew[5,2],bdnew[5,1],'go')
                plot(bdnew[10,2],bdnew[10,1],'mo')
                plot(bdr0[1,2],bdr0[1,1],'ro')
                plot(bdr0[5,2],bdr0[5,1],'go')
                plot(bdr0[10,2],bdr0[10,1],'mo')
                hold('off')
                axis('square')
                axis('equal')
        mbdpc=np.mean(bdpc,axis=0)
        bdrn=np.append([mbdpc[N:]],[mbdpc[0:N]],axis=0) # revise pt 5
    return bdpc, bnreg, sc, VamModel

def bdreg_main(df,N=None,VamModel=None,BuildModel=None):
    start = time.time() #record time
    bdpc, bnreg, sc, VamModel=bdreg_v1(df[0],N,VamModel,BuildModel)
    end = time.time()
    print 'For bdreg, elapsed time is ' + str(end-start) + 'seconds...'

    picklejar = os.path.abspath(os.path.dirname(__file__))
    picklejar = picklejar.replace('sourcecode','picklejar') + '/'
    df1 = pd.DataFrame(bdpc)
    df2 = pd.DataFrame(bnreg)
    df3 = pd.DataFrame(sc)
    df1.to_pickle(picklejar + 'bdpc.pickle')
    df2.to_pickle(picklejar + 'bnreg.pickle')
    df3.to_pickle(picklejar + 'sc.pickle')

    return bdpc, bnreg, sc, VamModel



'''
# bdreg_v1.m:79
        if plotres: #skip this for now
            figure(990)
            plot(bdrn[:,2],bdrn[:,1],'b-')
            hold('on')
            disp(mean(min(outyt,[],1)))
    if plotres: #skip this for now
        # show aligned image from random shuffle objects
        idr=rand(kll,1)
# bdreg_v1.m:90
        __,sidr=sort(idr,nargout=2)
# bdreg_v1.m:91
        for k in arange(1,30).reshape(-1):
            ktt=sidr[k]
# bdreg_v1.m:94
            bdd=bnreg[ktt]
# bdreg_v1.m:95
            bdd=matlabarray(cat(bdd[:,1],bdd[:,2]))
# bdreg_v1.m:96
            figure(88)
            plot(bdd[cat(arange(1,end()),1),2],bdd[cat(arange(1,end()),1),1],'b')
            hold('on')
'''
