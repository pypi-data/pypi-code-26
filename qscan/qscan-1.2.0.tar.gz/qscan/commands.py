""" Retrieving magnetic field data."""

from .settings import *
from .fortio   import *
from .main     import *
from .plots    import *
from .voigt    import *

def press(event):

    """
    Test
    """
    
    if event.xdata!=None:

        if event.key=='?':
            print '-------------------------------------------------------'
            print '    List of Commands'
            print '-------------------------------------------------------'
            print '<space> | scan the spectrum in velocity range'
            print ' <down> | decrease column density'
            print '   <up> | increase column density'
            print ' <left> | decrease Doppler parameter'
            print '<right> | increase Doppler parameter'
            print '    [/] | select left/right edge of blend region'
            print '    +/- | add/remove Voigt profile'
            print '      * | position of atmospheric lines'
            print '      = | select given Voigt profile'
            print '      . | show deuterium position at -82 km/s'
            print '      ? | list of commands'
            print '      a | select the anchor transition'
            print '      b | specify Doppler parameter'
            print '      c | include floating continuum'
            print '      d | delete all transitions'
            print '      e | select right edge of the fitting region'
            print '      f | save fitting regions in fort.13'
            print '      h | switch between HI and metal lists'
            print '      i | show information for selected regions'
            print '      l | identify region for blend searching'
            print '      n | specify column density'
            print '      p | move to given absorption redshift'
            print '      q | leave the program'
            print '      r | clear individual fitting region'
            print '      s | create PDF of the system'
            print '      v | move Voigt profile to selected position'
            print '      x | remove blending target region'
            print '      w | select left edge of the fitting region'
            print '      z | include floating zero'
            print '-------------------------------------------------------'
        if event.key==' ':
            scan(event,'scan')
            setup.fig.canvas.draw()
        if event.key=='.':
            setup.dtohflag = 1 if setup.dtohflag==0 else 0
            setup.edgeforce = [setup.ax.get_xlim(),setup.ax.get_ylim()]
            clf()
            gothrough()
            setup.fig.canvas.draw()
        if event.key=='*':
            setup.atmosphere = 1 if setup.atmosphere==0 else 0
            if setup.atmosphere==0: print '|- Remove positions of atmostpheric lines.'
            if setup.atmosphere==1: print '|- Display positions of atmostpheric lines.'
            print '|- Exit.'
            setup.edgeforce = [setup.ax.get_xlim(),setup.ax.get_ylim()]
            clf()
            gothrough()
            setup.fig.canvas.draw()            
        if event.key=='h':
            switch()
            setup.fig.canvas.draw()
        if event.key in ['w','e']:
            scan(event,'edge')
            setup.fig.canvas.draw()
        if event.key=='q':
            print '|- Exit.'
            close()
            quit()
        if (event.key in ['[',']']) or (event.key=='x' and setup.blendflag==1):
            scan(event,'blend')
            setup.fig.canvas.draw()
        if event.key=='i':
            info(event)
        if event.key=='p':
            zabs = raw_input('|- New redshift position z=')
            setup.zabs = float(zabs) if zabs!='' else setup.zabs
            scan(event,'scan')
            setup.fig.canvas.draw()
        if event.key=='s':
            print '|- Creating PDF of the system...'
            plotreg()
            print '|- PDF file created.'
        if event.key=='a':
            ypos  = event.ydata
            iatom = 0 if ypos<0 else -1 if ypos>=len(setup.atomlist) else int(str(ypos).split('.')[0])
            trans = setup.atomlist[iatom].split('_')[0]
            if setup.anchor==trans:
                print '|- Unset',setup.anchor,'as anchor transition.'
            else:
                setup.anchor = trans
                print '|- Anchor transition set to',setup.anchor
        if event.key=='c':
            scan(event,'continuum')
            setup.fig.canvas.draw()
        if event.key=='d':
            if np.array_equal(setup.atomreg,np.zeros((len(setup.atomlist),4),dtype=object))==False:
                try:
                    resp = raw_input('|- Are you sure you want to remove all regions? [Y/n] ')
                    if resp in ['','Y','y']:
                        scan(event,'delete')
                        setup.fig.canvas.draw()
                    else:
                        print '|- Fitting regions NOT removed.'
                except RuntimeError:
                    pass
        if event.key in ['b','n','+','-','left','right','up','down','v','=']:
            i = 0 if event.ydata<0 else -1 if event.ydata>=len(setup.atomlist) else int(str(event.ydata).split('.')[0])
            if event.key=='b' and len(setup.atomvoigt[i,1])>0:
                dop = raw_input('|- Doppler parameter b=')
                setup.dop = float(dop) if dop!='' else None
            if event.key=='n' and len(setup.atomvoigt[i,1])>0:
                col = raw_input('|- Column density N=')
                setup.col = float(col) if col!='' else None
            if event.key=='+' or (event.key in ['b','n','-','left','right','up','down','v','='] and len(setup.atomvoigt[i,1])>0):
                voigtcomp(event,i)
                setup.fig.canvas.draw()
        if event.key=='r':
            ypos  = event.ydata
            iatom = 0 if ypos<0 else -1 if ypos>=len(setup.atomlist) else int(str(ypos).split('.')[0])
            if setup.atomreg[iatom,0]!=0:
                try:
                    resp = raw_input('|- Are you sure you want to remove the region? [Y/n] ')
                    if resp in ['','Y','y']:
                        scan(event,'remove')
                        setup.fig.canvas.draw()
                    else:
                        print '|- Fitting region NOT removed.'
                except RuntimeError:
                    pass
        if event.key=='f':
            if np.array_equal(setup.atomreg,np.zeros((len(setup.atomlist),4),dtype=object))==False:
                print '|- Write fort.13 header...',
                savefort13()
                print 'done!'
                setup.fig.canvas.draw()
        if event.key=='z':
            scan(event,'zero')
            setup.fig.canvas.draw()
            
