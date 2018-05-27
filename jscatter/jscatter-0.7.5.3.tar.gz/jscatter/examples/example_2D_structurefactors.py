# coding=utf-8

# Crystal structure factors in 2D

# Comparison of different domainsizes dependent on direction of scattering ::

import jscatter as js
import numpy as np
# make xy grid in q space
R=8        # maximum
N=50       # number of points
qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
# add z=0 component
qxyz=np.c_[qxy,np.zeros(N**2)]
# create sc lattice which includes reciprocal lattice vectors and methods to get peak positions
sclattice= js.lattice.scLattice(2.1, 5)
# define crystal size in directions
ds=[[20,1,0,0],[5,0,1,0],[5,0,0,1]]
# We orient to 100 direction perpendicular to center of qxy plane
ffs=js.sf.latticeStructureFactor2D(qxyz,sclattice,orientation=[1,0,0],domainsize=ds,rmsd=0.1,hklmax=2)
fig=js.mpl.surface(qxyz[:,0],qxyz[:,1],ffs[3].array)
fig.axes[0].set_title('symmetric peaks: thiner direction perpendicular to scattering plane')
fig.show()
# We orient to 010 direction perpendicular to center of qxy plane
ffs=js.sf.latticeStructureFactor2D(qxyz,sclattice,orientation=[0,1,0],domainsize=ds,rmsd=0.1,hklmax=2)
fig2=js.mpl.surface(qxyz[:,0],qxyz[:,1],ffs[3].array)
fig2.axes[0].set_title('asymmetric peaks: thin direction is parallel to scattering plane')
fig2.show()


# Rotation of 10 degrees along [1,1,1] axis. It looks spiky because of low number of points in xy plane ::

import jscatter as js
import numpy as np
# make xy grid in q space
R=8    # maximum
N=800  # number of points
qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
# add z=0 component
qxyz=np.c_[qxy,np.zeros(N**2)] # as position vectors
# create sc lattice which includes reciprocal lattice vectors and methods to get peak positions
sclattice= js.lattice.scLattice(2.1, 5)
# We orient to 111 direction perpendicular to center of qxy plane
# this needs crystal rotation by 15 degrees to be alligned to xy plane after rotation to 111 direction
# The crystals rotates by 10 degrees around 111 to broaden peaks.
ds=15; fpi=np.pi/180.
ffs=js.sf.latticeStructureFactor2D(qxyz,sclattice,orientation=[1,1,1],
                                               rotation=[(30+15)*fpi,10*fpi,1,1,1],
                                               domainsize=ds,rmsd=0.1,hklmax=2,nGauss=23)
fig=js.mpl.surface(qxyz[:,0],qxyz[:,1],ffs[3].array)
fig.axes[0].set_title('10 degree rotation around 111 direction')
fig.show()

