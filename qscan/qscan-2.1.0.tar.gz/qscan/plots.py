from .settings import *
from .main     import *
from .voigt    import *
    
def plotreg():
    """
    Plot stored fitting region into PDF file.
    """
    mididx   = int(round(len(setup.atomlist)/2.))

    newatomlist1 = np.array(setup.atomlist[::-1][:mididx])
    newatomlist2 = np.array(setup.atomlist[::-1][mididx:])
    newatomlist  = np.empty((0,6))
    for i in range(mididx):
        newatomlist = np.vstack((newatomlist,newatomlist1[i]))
        if i<len(newatomlist2):
            newatomlist = np.vstack((newatomlist,newatomlist2[i]))
    setup.newatomlist = newatomlist

    newatomreg1 = np.array(setup.atomreg[::-1][:mididx])
    newatomreg2 = np.array(setup.atomreg[::-1][mididx:])
    newatomreg  = np.empty((0,4))
    for i in range(mididx):
        newatomreg = np.vstack((newatomreg,newatomreg1[i]))
        if i<len(newatomlist2):
            newatomreg = np.vstack((newatomreg,newatomreg2[i]))
    setup.newatomreg = newatomreg
    
    rc('font', size=10, family='sans-serif')
    rc('axes', labelsize=10, linewidth=0.2)
    rc('legend', fontsize=10, handlelength=10)
    rc('xtick', labelsize=7)
    rc('ytick', labelsize=7)
    rc('lines', lw=0.2, mew=0.2)
    rc('grid', linewidth=0.2)

    fig = figure(figsize=(8.27,11.69))
    axis('off')
    subplots_adjust(left=0.05, right=0.95, bottom=0.06, top=0.93, hspace=0, wspace=0.07)
    category = ' | Metal transitions | '
    title(setup.qsoname+' | z=%.5f'%setup.zabs+'\n',fontsize=10)
    specplot(fig)
    for Nplot in range(len(setup.newatomlist)):
      transplot(fig,Nplot)
    path = setup.qsoname+'/%.5f'%setup.zabs+'/'
    os.system('mkdir -p '+path)
    name = 'metals' if setup.atomlist[0,0]==setup.metallist[0,0] else 'lyman'
    savefig(path+name+'.pdf')
    close(fig)

def specplot(fig):
    """
    Plot whole spectrum with tickmark over each fitting region.
    """
    ymin = -0.1
    ymax = 1.2
    wmin = setup.wa[0]
    wmax = setup.wa[-1]

    Nrows = int(round(len(setup.newatomlist)/2))
    ax = fig.add_subplot(Nrows,1,1,xlim=[wmin,wmax],ylim=[ymin,ymax])
    ax.yaxis.set_major_locator(NullLocator())
    ax.xaxis.set_major_locator(NullLocator())
    ax.plot(setup.wa,setup.fl,'grey',lw=0.1)
    ax.plot(setup.wa,setup.er,'cyan',lw=0.1)
    ax.axhline(y=0,ls='dotted',color='grey',lw=0.2)
    ax.axhline(y=1,ls='dotted',color='grey',lw=0.2)
    ax.axhline(y=1,ls='dotted',color='grey',lw=0.2)
    for ionwave in setup.newatomlist[:,1]:
        ax.axvline(x=(setup.zabs+1)*float(ionwave), color='red', lw=0.5)
    xmin = 10*round(wmin/10)
    xmax = 10*round(wmax/10)
    if 10*round((xmax-xmin)/100)>0:
        ax.xaxis.set_major_locator(FixedLocator(np.arange(xmin,xmax,10*round((xmax-xmin)/100))))
    else:
        ax.xaxis.set_major_locator(FixedLocator([xmin,xmax]))

def transplot(fig,Nplot):
    """
    Plot each selected fitting region.
    """
    Nrows   = int(round(len(setup.newatomlist)/2.+2))
    ion     = setup.newatomlist[Nplot,0]+' %i'%float(setup.newatomlist[Nplot,1])
    watrans = float(setup.newatomlist[Nplot,1])*(setup.zabs+1)
    v       = (setup.c*((setup.wa-watrans)/setup.wa))
    vmin    = -setup.dv
    vmax    = setup.dv
    imin    = abs(v-vmin).argmin()
    imax    = abs(v-vmax).argmin()
    imin    = imin-1 if imin!=0 else imin
    imax    = imax+1
    y       = setup.fl[imin:imax]
    
    ax      = fig.add_subplot(Nrows,2,Nplot+5,xlim=[vmin,vmax],ylim=[-0.2,1.2])
    ax.xaxis.set_major_locator(FixedLocator(np.arange(-setup.dv,setup.dv+1,setup.dv/4)))
    ax.yaxis.set_major_locator(NullLocator())
    ax.plot(v[imin:imax],setup.fl[imin:imax],'black')
    ax.plot(v[imin:imax],setup.er[imin:imax],'cyan')
    ax.axhline(y=0,ls='dotted',color='grey',lw=0.2)
    ax.axhline(y=1,ls='dotted',color='grey',lw=0.2)
    ax.axvline(x=0,color='red',lw=0.8)

    vref  = (((setup.zabs+1)**2-1)/((setup.zabs+1)**2+1))*setup.c
    zpos1 = float(setup.newatomreg[Nplot,0]) / float(setup.newatomlist[Nplot,1]) - 1
    vpos1 = (((zpos1+1)**2-1)/((zpos1+1)**2+1))*setup.c
    vpos1 = (vpos1-vref)/(1-vpos1*vref/setup.c**2)
    zpos2 = float(setup.newatomreg[Nplot,1]) / float(setup.newatomlist[Nplot,1]) - 1
    vpos2 = (((zpos2+1)**2-1)/((zpos2+1)**2+1))*setup.c
    vpos2 = (vpos2-vref)/(1-vpos2*vref/setup.c**2)
    ax.axvspan(vpos1,vpos2,color='lime',alpha=0.7)
    
    t = ax.text(0.9*vmin,0.5,ion,color='blue',fontsize=8,va='center')
    t.set_bbox(dict(color='white', alpha=0.9, edgecolor=None))
    if Nplot<len(setup.newatomlist)-2:
        ax.xaxis.set_ticklabels([])
    else:
        ax.set_xlabel('Velocity relative to z='+str(round(setup.zabs,6))+' (km/s)',fontsize=9)
