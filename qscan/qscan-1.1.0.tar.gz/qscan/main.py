from .settings import *
from .voigt    import *

def gothrough():

    setup.flag = 1
    ax      = subplot(111,ylim=[0,len(setup.atomlist)])
    ionlab  = [setup.atomlist[i,0].replace(' ','')+' %i'%float(setup.atomlist[i,1]) for i in range(len(setup.atomlist))]
    iontick = np.arange(0.5,len(setup.atomlist)+0.5,1)
    yticks  = ax.set_yticklabels(ionlab)
    ax.yaxis.set_major_locator(FixedLocator(iontick))
    n = 0
    for i in range(len(setup.atomlist)):
        ionid  = setup.atomlist[i,0]
        ionwa  = float(setup.atomlist[i,1])
        z      = setup.wa/ionwa-1
        v      = (((z+1)**2-1)/((z+1)**2+1))*setup.c
        ax.plot(v,n+0.2+setup.fl*0.6,lw=0.8,alpha=0.8,color='black')
        if setup.atmosphere==1:
            for j in range(len(setup.atmolines)):
                imin = abs(setup.wa-setup.atmolines[j,0]).argmin()
                imax = abs(setup.wa-setup.atmolines[j,1]).argmin()
                if setup.edgeforce[0][0] < v[imin] and v[imax] < setup.edgeforce[0][1]:
                    ax.plot(v[imin:imax],n+0.2+setup.fl[imin:imax]*0.6,lw=5,alpha=0.5,color='magenta')
        if setup.blendflag==1:
            imin = abs(setup.wa-setup.wblendmin).argmin()
            imax = abs(setup.wa-setup.wblendmax).argmin()
            ax.plot(v[imin:imax],n+0.2+setup.fl[imin:imax]*0.6,lw=5,alpha=0.5,color='orange')
        if setup.atomreg[i,0]!=None or setup.atomreg[i,1]!=None:
            imin = abs(setup.wa-setup.atomreg[i,0]).argmin()
            imax = abs(setup.wa-setup.atomreg[i,1]).argmin()
            ax.plot(v[imin:imax],n+0.2+setup.fl[imin:imax]*0.6,lw=5,alpha=0.5,color='lime')
        ax.axhline(y=n+0.0,lw=0.1,color='black')
        ax.axhline(y=n+0.2,ls='dotted',lw=1,color='black')
        ax.axhline(y=n+0.8,ls='dotted',lw=1,color='black')
        ax.axhline(y=n+1.0,lw=0.1,color='black')
        n += 1
    setup.fig.suptitle(sys.argv[1]+'\nzabs=%.6f'%setup.z,fontsize=20)
    setup.ax = ax
    ionlist = []
    for i in range(len(setup.atomvoigt)):
        if setup.atomvoigt[i,0]!=0 and setup.atomlist[i,0] not in ionlist:
            voigtcomp(None,i)
            ionlist.append(setup.atomlist[i,0])            
    scan(None,'scan')
        
def switch():
    
    print '-------------------------------------------------------'
    if setup.atomlist[0,0]==setup.metallist[0,0]:
        print '    Switching to HI list'
        setup.atomlist   = setup.hydrolist
        setup.atomreg    = setup.hydroreg
        setup.atomvoigt  = setup.hydrovoigt
        setup.edgeforce  = [setup.ax.get_xlim(),setup.ax.get_ylim()]
        clf()
        gothrough()
    else:
        print '    Switching to Metal list'
        setup.atomlist  = setup.metallist
        setup.atomreg   = setup.metalreg
        setup.atomvoigt = setup.metalvoigt
        setup.edgeforce = [setup.ax.get_xlim(),setup.ax.get_ylim()]
        clf()
        gothrough()
    print '-------------------------------------------------------'

def scan(event,action):
    
    if action=='scan':

        vref  = (((setup.zprev+1)**2-1)/((setup.zprev+1)**2+1))*setup.c
        vmin  = setup.ax.get_xlim()[0]
        vmin  = (vmin-vref)/(1-vmin*vref/setup.c**2)
        vmax  = setup.ax.get_xlim()[1]
        vmax  = (vmax-vref)/(1-vmax*vref/setup.c**2)
        dv    = setup.dv if setup.flag==1 else (vmax-vmin)/2.
        vref  = event.xdata if event!=None and event.key==' ' else (((setup.zabs+1)**2-1)/((setup.zabs+1)**2+1))*setup.c
        setup.zabs = np.sqrt( (1+vref/setup.c) / (1-vref/setup.c) ) - 1
        setup.flag = 0

        vdeut = (vref+setup.shift)/(1+(setup.shift*vref)/setup.c**2)
        if event!=None: setup.zero.remove()
        setup.zero = setup.ax.axvline(x=vref,lw=2,color='red',alpha=0.5)
        if setup.dtohflag==1:
            if event!=None: setup.deut.remove()
            setup.deut = setup.ax.axvline(x=vdeut,lw=2,ls='dashed',color='blue',alpha=0.5)
 
        label = np.array(np.hstack((np.arange(0,-dv-1,-100)[::-1],np.arange(0,dv+1,100)[1:])),dtype=int)
        ticks = [(vref+i)/(1+(i*vref)/setup.c**2) for i in label]
        setup.ax.set_xticklabels(label)
        setup.ax.xaxis.set_major_locator(FixedLocator(ticks))

        if len(setup.edgeforce)==0:
            vmin = (vref-dv)/(1-(dv*vref)/setup.c**2)
            vmax = (vref+dv)/(1+(dv*vref)/setup.c**2)
            setup.ax.set_xlim(vmin,vmax)
            setup.ax.set_ylim(setup.ax.get_ylim())
        else:
            setup.ax.set_xlim(setup.edgeforce[0])
            setup.ax.set_ylim(setup.edgeforce[1])
            setup.edgeforce = []
        setup.zprev = setup.zabs
        setup.fig.suptitle(sys.argv[1]+'\nzabs=%.6f'%setup.zabs,fontsize=20)
        
    else:
        
        xpos   = event.xdata
        ypos   = event.ydata
        iatom  = 0 if ypos<0 else -1 if ypos>=len(setup.atomlist) else int(str(ypos).split('.')[0])
        trans  = setup.atomlist[iatom,0]+'%i'%float(setup.atomlist[iatom,1])
        warest = float(setup.atomlist[iatom,1])
        wacent = warest*(setup.zabs+1)
        wapos  = warest * np.sqrt( (1+xpos/setup.c) / (1-xpos/setup.c) )
        
    if action=='blend':
        
        if event.key=='x':
            
            print '|- Blending region removed.',
            setup.wblendmin = None
            setup.wblendmax = None
            setup.blendflag = 0

        else:
            
            wamin = setup.wblendmin if setup.wblendmin!=None else wacent
            wamax = setup.wblendmax if setup.wblendmax!=None else wacent
            if event.key=='[' and wapos<=wamax:
                waleft  = warest * np.sqrt( (1+xpos/setup.c) / (1-xpos/setup.c) )
                waright = wamax if wamax!=0 else wacent
            if event.key==']' and wapos<=wamin:
                waleft  = warest * np.sqrt( (1+xpos/setup.c) / (1-xpos/setup.c) )
                waright = wamax if wamax!=0 else wacent
            if event.key==']' and wapos>wamin:
                waleft  = wamin if wamin!=0 else wacent
                waright = warest * np.sqrt( (1+xpos/setup.c) / (1-xpos/setup.c) )
            if event.key=='[' and wapos>wamax:
                waleft  = wamin if wamin!=0 else wacent
                waright = warest * np.sqrt( (1+xpos/setup.c) / (1-xpos/setup.c) )
            print '|- Lookup blending region: %.2f A to %.2f A'%(waleft,waright)
            setup.wblendmin = waleft
            setup.wblendmax = waright
            setup.blendflag = 1
        
        setup.edgeforce = [setup.ax.get_xlim(),setup.ax.get_ylim()]
        clf()
        gothrough()
        
    if action=='continuum':

        if setup.atomreg[iatom,2]==0:
            setup.atomreg[iatom,2] = 1
            print '|- Floating continuum set for',trans,'%.2f'%warest
        else:
            setup.atomreg[iatom,2] = 0
            print '|- Floating continuum removed for',trans,'%.2f'%warest

    if action=='zero':

        if setup.atomreg[iatom,3]==0:
            setup.atomreg[iatom,3] = 1
            print '|- Floating zero set for',trans,'%.2f'%warest
        else:
            setup.atomreg[iatom,3] = 0
            print '|- Floating zero removed for',trans,'%.2f'%warest

    if action=='edge':
        
        wamin = setup.atomreg[iatom,0] if setup.atomreg[iatom,0]!=0 else wacent
        wamax = setup.atomreg[iatom,1] if setup.atomreg[iatom,1]!=0 else wacent
        
        if event.key=='w' and wapos<=wamax:
            waleft  = warest * np.sqrt( (1+xpos/setup.c) / (1-xpos/setup.c) )
            waright = wamax if wamax!=0 else wacent
        if event.key=='e' and wapos<=wamin:
            waleft  = warest * np.sqrt( (1+xpos/setup.c) / (1-xpos/setup.c) )
            waright = wamax if wamax!=0 else wacent
        if event.key=='e' and wapos>wamin:
            waleft  = wamin if wamin!=0 else wacent
            waright = warest * np.sqrt( (1+xpos/setup.c) / (1-xpos/setup.c) )
        if event.key=='w' and wapos>wamax:
            waleft  = wamin if wamin!=0 else wacent
            waright = warest * np.sqrt( (1+xpos/setup.c) / (1-xpos/setup.c) )
            
        print '|- Fitting region for '+trans+' : %.2f to %.2f A'%(waleft,waright)
        zmin  = waleft/warest-1
        dvmin = (((zmin+1)**2-1)/((zmin+1)**2+1))*setup.c
        zmax  = waright/warest-1
        dvmax = (((zmax+1)**2-1)/((zmax+1)**2+1))*setup.c
        
        x = np.arange(dvmin,dvmax,0.0001)
        y = np.array([iatom+1]*len(x))
        setup.atomreg[iatom,0] = waleft
        setup.atomreg[iatom,1] = waright
        setup.edgeforce = [setup.ax.get_xlim(),setup.ax.get_ylim()]
        clf()
        gothrough()
        
    if action=='remove':
        
        print '|-',trans,'removed from list of fitting regions.'
        setup.atomreg[iatom] = [0,0,0,0]
        setup.edgeforce = [setup.ax.get_xlim(),setup.ax.get_ylim()]
        clf()
        gothrough()
        
    if action=='delete':
        
        print '|- All transitions removed.'
        setup.atomreg = np.zeros((len(setup.atomlist),4),dtype=object)
        setup.edgeforce = [setup.ax.get_xlim(),setup.ax.get_ylim()]
        clf()
        gothrough()
        
def info(event):

    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    print '-------------------------------------------------------'
    print '    Transition information'
    print '-------------------------------------------------------'

    regs   = []
    qval   = []
    ypos   = event.ydata
    iatom  = 0 if ypos<0 else -1 if ypos>=len(setup.atomlist) else int(str(ypos).split('.')[0])
    trans  = setup.atomlist[iatom,0]+'%i'%float(setup.atomlist[iatom,1])
    warest = float(setup.atomlist[iatom,1])

    vref  = (((setup.zabs+1)**2-1)/((setup.zabs+1)**2+1))*setup.c
    vpos  = event.xdata
    zpos  = np.sqrt( (1+vpos/setup.c) / (1-vpos/setup.c) ) - 1
    wapos = warest * (zpos+1)
    vsep  = (vpos-vref)/(1-vpos*vref/setup.c**2)
    
    print '|-',trans,'rest-wavelength ...... {:>10} A'.format('%.4f'%warest)
    print '|-',trans,'observed wavelength .. {:>10} A'.format('%.4f'%(wapos))
    print '|-',trans,'redshift location .... {:>10}'.format('%.4f'%(zpos))
    print '|-',trans,'velocity position .... {:>10} km/s'.format('%.4f'%vsep)
    if isfloat(setup.atomlist[iatom,5]):
        print '|-',trans,'q-coefficient ........ {:>5}'.format('%i'%float(setup.atomlist[iatom,5]))
    if np.array_equal(setup.atomreg,np.zeros((len(setup.atomlist),4),dtype=object)):
        print '-------------------------------------------------------'
    else:
        print '-------------------------------------------------------'
        print '    Selected fitting regions'
        print '-------------------------------------------------------'
        if setup.anchor!=None:
            print '|- Anchor ion is',setup.anchor
        for i in range(len(setup.atomreg)):
            if setup.atomreg[i,0]!=setup.atomreg[i,1]:
                if isfloat(setup.atomlist[i,5]):
                    regs.append(setup.atomlist[i,0]+'%i'%float(setup.atomlist[i,1]))
                    qval.append(float(setup.atomlist[i,5]))
                print '|- {:<10}'.format(setup.atomlist[i,0]+'%i'%float(setup.atomlist[i,1])),
                print '| {:>5}'.format(setup.atomlist[i,5]),
                print '| {:>8} A'.format('%.2f'%setup.atomreg[i,0]),
                print '| {:>8} A'.format('%.2f'%setup.atomreg[i,1]),
                print '| C' if setup.atomreg[i,2]==1 else '',
                print '| Z' if setup.atomreg[i,3]==1 else ''
        if len(qval)>0:
            imin = qval.index(min(qval))
            imax = qval.index(max(qval))
            print '|- Lowest q transition ... :',regs[imin]
            print '|- Highest q transition .. :',regs[imax]
            print '|- q contrast ............ : %i'%abs(qval[imax]-qval[imin])
        print '-------------------------------------------------------'
        
