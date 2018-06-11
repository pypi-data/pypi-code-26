#!/usr/bin/env python3
# coding: utf-8

"""
===================
Wavelet MRTransform
===================

This example show how to clean images (remove NSB) using Wavelet transform
filtering.
"""

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

import pywicta
from pywicta.io import geometry_converter
from pywicta.io.images import image_generator
from pywicta.io.images import plot_ctapipe_image
from pywicta.denoising import wavelets_mrtransform
from pywicta.denoising.wavelets_mrtransform import WaveletTransform
from pywicta.denoising import inverse_transform_sampling
from pywicta.denoising.inverse_transform_sampling import EmpiricalDistribution

import ctapipe
from ctapipe.utils.datasets import get_dataset

###############################################################################
# Ignore warnings.

import warnings
warnings.filterwarnings('ignore')

###############################################################################
# Get images from ctapipe embedded datasets.

SIMTEL_FILE = get_dataset('gamma_test_large.simtel.gz')

###############################################################################
# Choose the instrument to use.

#cam_id = None
#cam_id = "ASTRICam"
#cam_id = "CHEC"
#cam_id = "DigiCam"
#cam_id = "FlashCam"
#cam_id = "NectarCam"
cam_id = "LSTCam"

###############################################################################
# Configure the trace integration as in the CTA Mars analysis.

integrator = 'LocalPeakIntegrator'
integration_correction = False

if cam_id == "ASTRICam":
    integrator_window_width = 1
    integrator_window_shift = 1
elif cam_id == "CHEC":
    integrator_window_width = 10
    integrator_window_shift = 5
elif cam_id == "DigiCam":
    integrator_window_width = 5
    integrator_window_shift = 2
elif cam_id == "FlashCam":
    integrator_window_width = 6
    integrator_window_shift = 3
elif cam_id == "NectarCam":
    integrator_window_width = 5
    integrator_window_shift = 2
elif cam_id == "LSTCam":
    integrator_window_width = 5
    integrator_window_shift = 2
else:
    raise ValueError('Unknown cam_id "{}"'.format(cam_id))

integrator_t0 = None
integrator_sig_amp_cut_hg = None
integrator_sig_amp_cut_lg = None
integrator_lwt = None

###############################################################################
# Get the 4th image of the dataset using pywicta image generator.

PATHS = [SIMTEL_FILE]
NUM_IMAGES = 5

#rejection_criteria = lambda image: not 50 < np.nansum(image.reference_image) < 200
rejection_criteria = None

it = image_generator(PATHS,
                     max_num_images=NUM_IMAGES,
                     cam_filter_list=[cam_id],
                     ctapipe_format=True,
                     time_samples=False,
                     mc_rejection_criteria=rejection_criteria,
                     integrator=integrator,
                     integrator_window_width=integrator_window_width,
                     integrator_window_shift=integrator_window_shift,
                     integrator_t0=integrator_t0,
                     integrator_sig_amp_cut_hg=integrator_sig_amp_cut_hg,
                     integrator_sig_amp_cut_lg=integrator_sig_amp_cut_lg,
                     integrator_lwt=integrator_lwt,
                     integration_correction=integration_correction)

image = next(it)  # This image is useless...
image = next(it)  # This image is useless...
image = next(it)  # This image is useless...
image = next(it)

###############################################################################
# Plot the selected image with NSB.

geom1d = geometry_converter.get_geom1d(image.meta['cam_id'])

title_str = "{} (run {}, event {}, tel {}, {:0.2f} {})".format(image.meta['cam_id'],
                                                               image.meta['run_id'],
                                                               image.meta['event_id'],
                                                               image.meta['tel_id'],
                                                               image.meta['mc_energy'][0],
                                                               image.meta['mc_energy'][1])

plot_ctapipe_image(image.input_image, geom=geom1d, plot_axis=False, title=title_str)
plt.show()

###############################################################################
# Plot the selected image with NSB after the geometric transformation.

image_2d = geometry_converter.image_1d_to_2d(image.input_image, image.meta['cam_id'])

plt.imshow(image_2d)
plt.show()

###############################################################################
# Fill blank pixels with noise.

noise_cdf_file = inverse_transform_sampling.get_cdf_file_path(cam_id)  # pywicta.denoising.cdf.LSTCAM_CDF_FILE
print(noise_cdf_file)
noise_distribution = EmpiricalDistribution(noise_cdf_file)

###############################################################################
# Cleaning the image with Wavelets transform filtering.

#TMP_DIR = "/Volumes/ramdisk"
TMP_DIR = "."

wavelet = WaveletTransform()
cleaned_image = wavelet.clean_image(image_2d,
                                    type_of_filtering = 'hard_filtering',
                                    filter_thresholds = [8, 2],            # <- TODO
                                    last_scale_treatment = "mask",
                                    detect_only_positive_structures = False,
                                    kill_isolated_pixels = False,
                                    noise_distribution = noise_distribution,
                                    tmp_files_directory = TMP_DIR)

###############################################################################
# Plot the cleaned image.

plt.imshow(cleaned_image)
plt.show()

cleaned_image_1d = geometry_converter.image_2d_to_1d(cleaned_image, image.meta['cam_id'])

plot_ctapipe_image(cleaned_image_1d, geom=geom1d, plot_axis=False, title=title_str)
plt.show()
