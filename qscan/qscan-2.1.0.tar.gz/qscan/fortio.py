from .settings import *
from .voigt    import *

def readfort13():
    """
    Read input fort.13 and store parameters in global variables.
    """
    flag   = 0
    fort13 = numpy.loadtxt(setup.fort,delimiter='\n',dtype=str)
    for line in fort13:
        if '*' in line:
            flag += 1
        elif flag==1:
            wmin = float(line.split()[2])
            wmax = float(line.split()[3])
            ion  = line.split('!')[1].split()[0]
            rest = float(line.split('!')[1].split()[1])
            if ion=='HI':
                dif = numpy.array([abs(float(k)-rest) for k in setup.hydrolist[:,1]])
                idx = numpy.where(numpy.logical_and(setup.hydrolist[:,0]==ion,dif<1))[0]
                setup.hydroreg[idx] = [wmin,wmax,0,0]
            else:
                dif = numpy.array([abs(float(k)-rest) for k in setup.metallist[:,1]])
                idx = numpy.where(numpy.logical_and(setup.metallist[:,0]==ion,dif<1))[0]
                setup.metalreg[idx] = [wmin,wmax,0,0]
        elif flag==2:
            l   = line.split('!')[0].split()
            ion = l[0]+l[1] if len(l[0])==1 else l[0]
            N   = l[2]      if len(l[0])==1 else l[1]
            N   = float(re.compile(r'[^\d.-]+').sub('',N))
            z   = l[3]      if len(l[0])==1 else l[2]
            z   = float(re.compile(r'[^\d.-]+').sub('',z))
            b   = l[4]      if len(l[0])==1 else l[3]
            b   = float(re.compile(r'[^\d.-]+').sub('',b))
            if ion=='HI':
                for i in range(len(setup.hydrovoigt)):
                    if setup.hydrolist[i,0]==ion:
                        setup.hydrovoigt[i,0] = None
                        setup.hydrovoigt[i,1] = np.vstack((setup.hydrovoigt[i,1],[[],[],z,N,b]))
            if ion!='HI':
                for i in range(len(setup.metalvoigt)):
                    if setup.metallist[i,0]==ion:
                        setup.metalvoigt[i,0] = None
                        setup.metalvoigt[i,1] = np.vstack((setup.metalvoigt[i,1],[[],[],z,N,b]))
            setup.zcomp = z

def savefort13():
    """
    Save identified absorption system into customised fort.13.
    """    
    path    = setup.qsoname+'/%.5f'%setup.zabs+'/'
    os.system('mkdir -p '+path)
    head    = open(path+'header.dat','w')
    out     = open(path+'fort.13','w')
    mod     = 1 if '--turbulent' in sys.argv else 0
    ionlist = []
    out.write('   *\n')
    atomlist  = numpy.vstack((setup.metallist[::-1] ,setup.hydrolist[::-1] ))
    atomreg   = numpy.vstack((setup.metalreg[::-1]  ,setup.hydroreg[::-1]  ))
    atomvoigt = numpy.vstack((setup.metalvoigt[::-1],setup.hydrovoigt[::-1]))
    for i in range(len(atomlist)):
        if atomreg[i,0]!=atomreg[i,1]:
            path  = sys.argv[1]
            left  = '%.2f'%float(atomreg[i,0])
            right = '%.2f'%float(atomreg[i,1])
            vsig  = 'vsig=2.5'
            head1 = atomlist[i,0]+'_%.2f'%float(atomlist[i,1])
            head2 = atomlist[i,0]+' %.2f'%float(atomlist[i,1])
            head.write(head1+'\n')
            out.write(path+'    1    '+left+'   '+right+'   '+vsig+'   ! '+head2+'\n')
    out.write('  *\n')
    for i in range(len(atomlist)):
        if atomreg[i,0]!=atomreg[i,1]:
            ion   = atomlist[i,0]
            ion   = '{0:<6}'.format(ion)
            cond1 = ion not in ionlist
            cond2 = setup.anchor!=None and atomlist[i].split('_')[0]==setup.anchor
            cond3 = setup.anchor==None and len(ionlist)==0
            if len(atomvoigt[i,1])>0:
                for j in range(len(atomvoigt[i,1])):
                    z = atomvoigt[i,1][j,2]
                    N = atomvoigt[i,1][j,3]
                    b = atomvoigt[i,1][j,4]
                    if cond1 and (cond2 or cond3) and j==0:
                        out.write('   '+ion+'   %.5f     %.7faa   %.4fla     0.00E+00q       0.00   %i.00E+00  0 !    1\n'%(N,z,b,mod))
                    else:
                        out.write('   '+ion+'   %.5f     %.7fAA   %.4fLA     0.00E+00q       0.00   %i.00E+00  0 !    1\n'%(N,z,b,mod))
            elif cond1 and (cond2 or cond3):
                out.write('   '+ion+'   15.00000     %.7faa   10.0000la     0.00E+00q       0.00   %i.00E+00  0 !    1\n'%(setup.zabs,mod))
            elif cond1:
                out.write('   '+ion+'   15.00000     %.7fAA   10.0000LA     0.00E+00Q       0.00   %i.00E+00  0 !    1\n'%(setup.zabs,mod))
            ionlist.append(ion)
    for i in range(len(atomlist)):
        midred = ((float(atomreg[i,0])+float(atomreg[i,1]))/2.) / 1215.6701 - 1
        if atomreg[i,-2]==1 and atomreg[i,0]!=atomreg[i,1]:
            out.write('   <>        1.00000     %.7f      0.0000FF   0.00E+00FF      0.00   0.00E+00  0 !    1\n'%midred)
        if atomreg[i,-1]==1 and atomreg[i,0]!=atomreg[i,1]:
            out.write('   __        0.00000     %.7f      0.0000FF   0.00E+00FF      0.00   0.00E+00  0 !    1\n'%midred)
    out.close()
    head.close()
    
