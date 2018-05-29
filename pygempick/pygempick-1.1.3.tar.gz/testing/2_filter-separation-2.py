#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 18:10:30 2018

@author: joseph
"""
##change parameters of blob detection
##add more thresholds to compare 
##for each test 
import cv2
import glob
import numpy as np
import pygempick.modeling as mod
import pygempick.core as py
import matplotlib.pyplot as plt


images = glob.glob('/media/joseph/Joe\'s USB/05.08.2018/Joe Trial/R10_compressed/*.jpg')

#do this for sets of 10 images... 
#combine all the images with values on them into one set... 

N = len(images) #number of images in our set!!!
name = input('Name this image set: ')
i=0
t3=0

#Starting counter for set filters
pstatic = np.arange(18,24)

plt.figure()

for num in pstatic:
    
    picked = 0  
    duplicates = 0
    i = 0
    
    for image in images[:100]:
        
        orig_img = cv2.imread(image) ##reads specific test file
        
        output2 = py.hlog_filt(num, orig_img, 'no')
        keypoints_log = py.pick(output2, 31, .83, .61 , .61, 0)
        
        p = np.arange(1,31,2) #ranges of anchor value in filtering kernel

        count, dup = mod.septest2(p, orig_img, keypoints_log)
        
        picked += count
        duplicates += dup
        
        
        i+=1
        
        if i%2==0:
            print('Done image {} of {}'.format(i,N))


    plt.title('2 Fold Filter Separation Power of AB Aggregate w/ Varying Hclap Anchor ')
    plt.xlabel('SCALING FACTOR \'p\'')
    plt.ylabel('Detected Particles')
    plt.plot(p, picked, '.--', label='HLOG-{}'.format(num))
    plt.plot(p, duplicates, 'x', label='DUP-{}'.format(num))
    plt.legend(loc='best')
    plt.grid(True)

plt.savefig('separation_{}.png'.format(name))
'''
Use the Anti to optimize?
There is variation of picking between methods - finally create one with simple
binary thresholding as a negative control - should be inconsistent as background 
conditions varry...

Set of 10:
draw picked image - lap ring w/green, DOG solid circle in blue
(...control pick with regular binary thresholding...)

#more particles allow for better optimization of the algorithm.
However, in many data sets due to the high resolution and low solute concentrations
in question the # of particles detected varry...

pan specific case - antibody that detects all aTTr forms (normal & diseased)
Cetux - cancer drug (shouldn't see any) - subtract this number as background
H14G1 - specific to misfoolded form of attr. 

One set - (more will come in the future) = need more pan specific 

##see if you can run with similar parameters - how would the result(s) change?

ie 22 .88 .81 .81 for all cetux
ie 20 .83 .73 .73 for all H14G8-mis-ttr
ie 20 .8 .7 .7 for all Anti-poly-ttr

First 100 images of diseased & normal sets were used in the separation tests of
the filter...(We've recived atter )

After the end of the filtering - show the efficiency of picking...across 200 
fabricated with different particles drawn on each... 

Seen similar results when drawn circles vs ellipse(s)...

'''

