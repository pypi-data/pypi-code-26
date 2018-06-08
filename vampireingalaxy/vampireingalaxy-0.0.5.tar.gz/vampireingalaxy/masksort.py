#! C:\\Python27

import os
import time
import re

import pandas as pd
import numpy as np
import imageio
#from scipy import misc
################################
# How this script works #
# 1. read binary masks <- output of segmentation by cell profiler
# 2. compare with centroid recorded in a csv file
# 3. label the masks to the corresponding original image
# 4. organize masks into a subfolder named after original image
################################
# Detailed explanation #
# Reading entire set of mask is heavywork, we first compare object #1 with centroid #1 of set 1,2,...n.
# note: comparing means see if mask has light intensity at the centroid
# If we are "unlucky", there could be two masks from two different sets overlap, then we compare object #2,3,...
# the timestamp for the same set varies as hundreds of mask cannot be generated simultaneously
# this is trouble in labeling masks that have different timestamp then the masks compared with centroid
# I used clustering of timestamp in addition to labeling the first timestamp of each cluster
# Thus, robust classification is achieved....
################################
# Assumptions #
# 1. csv name is always Cells.csv  Note: csv can be named in cell profiler, we assure the user not to touch this in cell profiler.
# 2. user knows where binary files are stored
# 3. the number of objects in a raw image is less than 9999
################################
def read_location(csv,objectnum):
	x = csv.Location_Center_X
	y = csv.Location_Center_Y
	objnum = csv.ObjectNumber
	index = np.where(objnum == objectnum+1)[0] #first object location
	x = x[index].fillna(0).astype(int).as_matrix()
	y = y[index].fillna(0).astype(int).as_matrix()
	return x,y

def read_nth_object_mask(dirname,masknames):
	mask_matrix = []
	for mask in masknames:
		#im = misc.imread(dirname + mask)
		im = imageio.imread(dirname + mask,format=None)
		mask_matrix.append(im)
	return mask_matrix

def check_location_in_mask(locx,locy,mask_matrix,masknames):
	imagenum=[]
	corresmask=[]
	for i in range(len(locx)):
		matched_mask=[]
		x= locx[i]
		y= locy[i]

		for j in range(len(mask_matrix)):
			maskinuse = np.divide(mask_matrix[j],255)
			intensity = maskinuse[y][x]
			if intensity == 1:
				matched_mask.append(masknames[j])

		if len(matched_mask) == 0:
			locresult = None
			status = 'inconclusive'
		elif len(matched_mask) == 1:
			#register mask name in matched_mask [x.tiff,y.tiff,z.tiff]
			corresmask.append(matched_mask)
			#register order in image num [1,2,3,4,...]
			imagenum.append([i+1])
			#put index and maskname in a 2d array
			locresult = np.append([imagenum],[corresmask],axis=0)
			status = 'conclusive'
		elif len(matched_mask) > 1:
			locresult = None
			status = 'inconclusive'
		
	return locresult, status

def sortimage(res,dirname,directory):#resminus,res0,res1,res2,res3
	unicodelist = os.listdir(dirname)
	stringlist = [x.encode('UTF8') for x in unicodelist]
	for i in range(len(res)):
		movelist = [_ for _ in stringlist if res[i] in _]
		for filename in movelist:
			current = dirname + filename
			destination = directory + filename
			os.rename(current,destination)

def sortset(no_objects_per_set,dirname):
	foldername = [_ for _ in os.listdir(dirname) if 'image' in _]
	for idx,obj in enumerate(no_objects_per_set):
		dst  = dirname+ 'set ' + str(idx+1) +'/'
		if not os.path.isdir(dst):
			os.makedirs(dst)
		for i in range(obj):
			current = dirname + foldername[0]
			destination = dst + foldername[0]
			os.rename(current,destination)
			del foldername[0]

def grouper(iterable,startingnum):
	prev = None
	group = []
	cut = 1
	for item in iterable:
		if not prev or item - prev <= 1 and item < startingnum[cut]:
			group.append(item)
		else:
			if cut < len(startingnum):
				cut = cut + 1
			yield group
			group = [item]
		prev = item
	if group:
		yield group

def clusterer(dirname,no_images,locresult):
	masks = [_ for _ in os.listdir(dirname) if '.tiff' in _]
	numbers=set()
	for idx,obj in enumerate(masks):
		res = re.findall("_([0-9]{10}).tiff",obj)[0]
		numbers.add(res)
	numbers = list(numbers)
	numbers = [x.encode('UTF8') for x in numbers]
	numbers = np.sort(np.asarray(numbers).astype(int))

	startingnum = []
	for i in range(no_images):
		fullname = locresult[1][i][0]
		res = re.findall("_([0-9]{10}).tiff",fullname)[0]
		res = int(res)
		startingnum.append(res)
	startingnum.append(9999999999)
	startingnum = np.sort(startingnum)
	cluster = dict(enumerate(grouper(numbers,startingnum), 1))
	if len(cluster) != no_images:
		#sort error
		return None
	return cluster


##### check first mask with centroid, and then if there are two masks overlapping, move on to object #2,3,..

def masksort(dirname):
	csv = pd.read_csv(dirname + 'Cells.csv') #later replace filename automatically
	longest_obj = max(csv.ObjectNumber)
	setnum = csv.Metadata_SetNumber
	no_sets = max(setnum)
	imagenum = csv.ImageNumber
	no_images = max(imagenum)
	no_objects_per_set = []
	for sets in range(no_sets):
		index = np.argwhere(setnum == sets+1).flatten()
		if sets == 0 :
			no_objects_in_a_set = max(imagenum[index])
		else: no_objects_in_a_set = max(imagenum[index]) - no_objects_per_set[sets-1]
		no_objects_per_set.append(no_objects_in_a_set)

	#for loop here
	for objectnum in range(longest_obj):
		print 'iteration' + str(objectnum + 1) + '/' + str(longest_obj)
		masknames = []
		masklist = [_ for _ in os.listdir(dirname) if str(objectnum+1) + "_" in _]
		if objectnum < 9:
			for fname in masklist:
				res = re.search("_([0]{3}[0-9])_",fname) #find two digit names
				if not res==None: masknames.append(fname)
		if objectnum > 8 and objectnum <99:
			for fname in masklist:
				res = re.search("_[0]{2}([0-9]{2})_",fname) #find two digit names
				if not res==None: masknames.append(fname)
		if objectnum > 98 and objectnum <999:
			for fname in masklist:
				res = re.search("_[0]([0-9]{3})_",fname) #find two digit names
				if not res==None: masknames.append(fname)
		if objectnum > 998:
			for fname in masklist:
				res = re.search("_([0-9]{4})_",fname) #find two digit names
				if not res==None: masknames.append(fname)
		mask_matrix = read_nth_object_mask(dirname,masknames) #read masks in directory as 3d arrays
		locx,locy = read_location(csv,objectnum) #read location of first masks of each image
		locresult,status = check_location_in_mask(locx,locy,mask_matrix,masknames) #compare location with each mask and determine corresponding mask
		#locresult is a list of pair of objectnum and mask filename

		if status == 'inconclusive': continue
		elif status == 'conclusive':
			print 'saving after ' + str(objectnum+1) + 'th object verification'
			#clustering timestamp
			cluster = clusterer(dirname,no_images,locresult)
			if cluster == None:
				print 'sort error!'
				return()
			#save
			for i in range(no_images): #repeat 4 times now
				directory = dirname +'image' + str(i+1) +'/'
				if not os.path.exists(directory):
					os.makedirs(directory)
				fullname = locresult[1][i][0]
				#similar time grouping <--- this need to be replaced with better method: check unix time excel export from cell profiler
				res = re.findall("_([0-9]{10}).tiff",fullname)[0]
				res = int(res) #convert res from unicode to int to compare with cluster of int
				#cluster was converted into int to sort the timestamp
				res = [x for x in cluster.values() if res in x][0]
				res = [str(x) for x in res]
				sortimage(res,dirname,directory)
			sortset(no_objects_per_set,dirname)
			return()

#start=time.time()
#main()
#end=time.time()
#print 'elapsed time is ' + str(end-start) + 'seconds...'
