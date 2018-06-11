#!/usr/bin/env python3
# coding: utf-8

"""
===================
Get ctapipe dataset
===================

This example show how to get images from ctapipe embedded datasets using
pywicta image generator and how to print them with pywicta plot functions.
"""

import pywicta
from pywicta.io import geometry_converter
from pywicta.io.images import image_generator
from pywicta.io.images import plot_ctapipe_image

import ctapipe
from ctapipe.utils.datasets import get_dataset

import matplotlib.pyplot as plt

###############################################################################
# Ignore warnings.

import warnings
warnings.filterwarnings('ignore')

###############################################################################
# Print the list of available ctapipe extra resources.

print(ctapipe.utils.datasets.find_all_matching_datasets(''))

###############################################################################
# Get images from ctapipe embedded datasets.

#SIMTEL_FILE = get_dataset('gamma_test.simtel.gz')
SIMTEL_FILE = get_dataset('gamma_test_large.simtel.gz')

###############################################################################
# Get dataset images using pywicta image generator.

PATHS = [SIMTEL_FILE]
NUM_IMAGES = 3

CAM_FILTER_LIST = None
#CAM_FILTER_LIST = ["LSTCam"]

it = image_generator(PATHS,
                     max_num_images=NUM_IMAGES,
                     ctapipe_format=True,
                     time_samples=False,
                     cam_filter_list=CAM_FILTER_LIST)

###############################################################################
# Plot some images in the gamma test dataset using pywicta plot functions.

for image in it:
    title_str = "{} (run {}, event {}, tel {}, {:0.2f} {})".format(image.meta['cam_id'],
                                                                   image.meta['run_id'],
                                                                   image.meta['event_id'],
                                                                   image.meta['tel_id'],
                                                                   image.meta['mc_energy'][0],
                                                                   image.meta['mc_energy'][1])
    geom1d = geometry_converter.get_geom1d(image.meta['cam_id'])
    
    # Plot the image with NSB
    plot_ctapipe_image(image.input_image, geom=geom1d, plot_axis=False, title=title_str)
    plt.show()
    
    # Plot the image without NSB
    plot_ctapipe_image(image.reference_image, geom=geom1d, plot_axis=False, title=title_str)
    plt.show()
