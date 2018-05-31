import h5py as h5
import numpy as np
import os
import math


def readArray(fileType, directory, tag, arrayType):
	"""
	Read out an array from EAGLE simulation data.
	Parameters
	----------
	filetype : string
		Filetype to read
	directory : string
	    Snapshot directory
	tag : string
		Snapshot tag
	arrayType : string
		Which array to read from the file
	See Also
	--------
	
	Examples
	--------
	>>> galaxyPos = re.readArray('SNAPSHOT', 'snapshots', '028_z000p000', '/PartType0/Coordinates')
	
	"""
	array = np.array([],dtype=float)
	fileList = sorted(os.listdir(directory + "/" + fileType.lower() + "_" + tag + "/"), key=lambda a: int(a.split(".")[1]))#This sorting is super important
	for fileName in fileList:
		if tag in fileName:
			file = h5.File(directory + "/" + fileType.lower() + "_" + tag + "/" + fileName,'r')
			if len(array) != 0:
				array = np.append(array,file[arrayType],axis=0)
			else:
				array = np.array(file[arrayType],dtype=float)
	return array


def projectionMatrix(los):
	"""
	Read out an array from EAGLE simulation data.
	Parameters
	----------
	los : array_like
		Normalised line of sight vector, [x,y,z]
	See Also
	--------
	
	Examples
	--------
	>>> projMat = projectionMatrix([1,0,0])
	
	"""
	
	L1=np.array([0,1,0],dtype=float)
	L2=np.array([0,0,1],dtype=float)

	

	
	if not np.dot(los,[1,0,0]) in [1,-1]:
		#Prevents the line of sight vector being in the same plane as the basis vectors.
		if 0 in np.sum([los,L1,L2],axis=0):
			L2=np.array([1,0,0],dtype=float)
			
		#Find some starting vectors which do not conflict with the line of sight vector.
		if  np.dot(los,[0,1,0]) in [1,-1]:
				L1=np.array([1,0,0],dtype=float)
				L2=np.array([0,0,1],dtype=float)

		elif np.dot(los,[0,0,1]) in [1,-1]:
				L1=np.array([1,0,0],dtype=float)
				L2=np.array([0,1,0],dtype=float)
		else:
			#Gramm-Schmidt Process
			L1=np.subtract(L1,(np.dot(L1,los)*los))
			L1=L1/np.linalg.norm(L1)
			L2a=np.subtract(L2,(np.dot(L2,L1)*L1))
			L2=np.subtract(L2a,(np.dot(L2,los)*los))
			L2=L2/np.linalg.norm(L2)

#This is a super dodgy way of achieving something for a rotation animation I made. 
#If you change the observation position in the x-z plane it should keep the vectors orientated correctly.
#Specifically when moving in a circle centred on the object to be observed in the x-z plane.
	if los[0] > 0 and los[2] >= 0:
		if L2[0] <= 0:
			L2 = -1*L2
	if los[0] > 0 and los[2] < 0:
		if L2[0] > 0:
			L2 = -1*L2
	if los[0] <= 0 and los[2] < 0:
		if L2[0] > 0:
			L2 = -1*L2
	if los[0] < 0 and los[2] > 0:
		if L2[0] < 0:
			L2 = -1*L2

	array = np.concatenate(([L1], [L2],[[0,0,0]]))#Make the third row los
	return array


def spectralCube(obsv, directory, tag, centre, fileType='SNAPSHOT', HIFracFile='', H0=72.e3, speedLight=3e8, offset=[0,0], sides=[-1,0,0], rotation=0.0, coordConvFact=1., velConvFact=1., raDec=False, cut='none'):
	"""
	Create a HI spectral cube from an EAGLE snapshot.
	Parameters
	----------
	observation : array_like
	    Observation point in the space, [x,y,z]
	directory : string
	    Snapshot directory
	tag : string
		Snapshot tag
	centre : array_like
		Point to which the observation is centred, [x,y,z]
	filetype : string, optional
		If not provided defaults to 'SNAPSHOT'
	HIFracFile : string, optional
		HDF5 file to get the fraction of H which is HI in the particles.
	H0 : float, optional
		Huble constant in m/s/Mpc. Defaults to 72*10^3m/s/Mpc
	speedLight : float, optional
		Speed of light for Doppler shift. Defaults to 3*10^8m/s
	offset : array_like, optional
		Offset for cutting x,y. Defaults to [0,0]
	sides : array_like, optional
		Side length of box to cut
	rotation : float, optional
		Angle to rotate image by in radians. Clockwise
	coordConvFact : float, optional
		Conversion factor from comoving coordinates. h in simlulations. 
	velConvFact : float, optional
		Conversion factor from comoving velocities. a in simlulations. 
	raDec : boolean, optional
		If true, positions are given in equitorial coordinates, Right Acension and Declination.
	cut : string, optional
		The type of cut to make of the data, view, region or none. Region cuts a square prism
	See Also
	--------
	

	Examples
	--------
	>>> [projection, frequency, radialVel, projMat, lineOfSight] = re.spectralCube(obsvPos, directory, tag, galaxyCentre, sides=[0.03,0.03], coordConvFact=0.677)
	
	"""

	#Read in the arrays
	position = coordConvFact * readArray(fileType, directory, tag, '/PartType0/Coordinates')
	velocities = velConvFact * readArray(fileType, directory, tag, '/PartType0/Velocity') * 1e3
	mass = coordConvFact * readArray(fileType, directory, tag, '/PartType0/Mass') #I have no idea if this is correct but it seems to be, using the coordConvFact that is
	H_Mass = np.multiply(mass, readArray(fileType, directory, tag, '/PartType0/ElementAbundance/Hydrogen'))



	displacement = np.subtract(centre,obsv)
	lineOfSight = np.array(displacement/np.linalg.norm(displacement),dtype=float)	
	projMat = projectionMatrix(lineOfSight)

	posShifted = np.subtract(position,obsv)
	projection = np.matmul(posShifted,projMat.T)

	#Rotate the points
	rotationMatrix = np.array([[np.cos(rotation), -np.sin(rotation)],[np.sin(rotation),np.cos(rotation)],[1,1]])
	projection = np.matmul(projection,rotationMatrix)

	velocities = velocities	
	radialVel = np.nan_to_num(np.matmul(velocities,lineOfSight) + H0 * np.matmul(posShifted,lineOfSight))

	if not cut == 'none' and not (sides[0] < 0):
		if cut == 'region':
			indices = inRegion(posShifted,displacement,sides)[1]
			projection=projection[indices,:]
		elif cut == 'view':
			[projection,indices] = inView(projection,sides[0:2],offset)
		else:
			indices = np.linspace(0, len(projection) - 1, len(projection)).astype(int)
	else:
		indices = np.linspace(0, len(projection) - 1, len(projection)).astype(int)

	radialVel = radialVel[indices]

	freq0 = 1420.41#HI frequency in MHz
	frequency = (1-radialVel/speedLight)*freq0

	if raDec:
		projection = projection / np.linalg.norm(posShifted[indices,:],axis=1)[:,None]
		projection = np.array([projection[:,0]/(2*math.pi)*24,projection[:,1]*180/math.pi]).T


	if not HIFracFile == '':
		HI_Frac = np.asarray(h5.File(directory +'/' + HIFracFile +'.hdf5','r')['BR06_HI_Fraction'])
		
		HI_Mass = np.multiply(H_Mass[indices], HI_Frac[indices])
	else:
		HI_Mass = H_Mass[indices]


	return [projection, frequency, HI_Mass, radialVel, projMat, lineOfSight]


def inRegion(data,centre,sides):
	"""
	Cut out a box from the data, centred around centre with side lengths 2*sides
	----------
	data : array_like
		Data to cut from
	centre : array_like
		Position of the centre of the box
	sides : array_like
		Half the side lengths of the box
	See Also
	--------
	
	Examples
	--------
	>>> [galaxyPos,indices] = inRegion(data,centre,[0.02,0.02,0.02])
	
	"""
	indices = np.where((data[:,0] >= centre[0]-sides[0])
		& (data[:,0] <= centre[0]+sides[0]) 
		& (data[:,1] >= centre[1]-sides[1]) 
		& (data[:,1] <= centre[1]+sides[1]) 
		& (data[:,2] >= centre[2]-sides[2]) 
		& (data[:,2] <= centre[2]+sides[2]))[0]


	dataOut = data[indices,:]

	return [dataOut,indices]


def inView(data, sides, offset=[0,0]):#Cuts about [0,0,0], hence offset makes sense here
	"""
	Cut out data outside of view, bounded by sides in X-Y plane
	----------
	data : array_like
		Data to cut from
	sides : array_like
		Half the side lengths of the box
	offset : array_like, optional
		Offset from the origin
	See Also
	--------
	
	Examples
	--------
	>>> [galaxyPos,indices] = inView(data,centre,[0.02,0.02,0.02])
	
	"""
	indices = np.where((data[:,0] >= -sides[0]+offset[0]) 
		& (data[:,0] <= sides[0]+offset[0]) 
		& (data[:,1] >= -sides[1]+offset[1]) 
		& (data[:,1] <= sides[1]+offset[1]))[0]

	dataOut = data[indices,:]

	return [dataOut,indices]


#
def findCentre(data,guess,sides,tolerance,iterMax=1e+3):
	"""
	Find the centre of mass of an object given some initial approximation.
	Uses the fact that a higher density region will tend to be the centre of
	mass the more it takes up a region ie. Finds a local minimum of the centre of mass
	when viewed as small region. 
	----------
	data : array_like
		Data to cut from
	guess : array_like
		Rough guess of the centre
	sides : array_like
		Half the side lengths of the box. Should be just larger than the object in question.
	tolerance : float
		Tolerance level, smaller values have less error
	iterMax : int, optional
		Maximum number of iterations, defaults to 1000 
	See Also
	--------
	
	Examples
	--------
	>>> galaxyCentre = re.findCentre(galaxyPos, galaxyPos.mean(axis=0), region, 1e-8)
	
	"""

	previous = inRegion(data,guess,sides)[0].mean(axis=0)
	centre = guess
	iterations = 0

	while (all(i >= tolerance for i in np.absolute(np.subtract(centre,previous))) and iterations < iterMax):
		previous = centre
		[galaxyPos,indices] = inRegion(data,centre,sides)
		centre = galaxyPos.mean(axis=0)
		iterations += 1

	if iterations >= iterMax:
		raise StopIteration('Did not converge within iteration limit')
	return centre
