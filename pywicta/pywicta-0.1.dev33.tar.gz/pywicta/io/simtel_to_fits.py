#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Jérémie DECOCK (http://www.jdhp.org)

# This script is provided under the terms and conditions of the MIT license:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
... TODO
"""

__all__ = ['extract_images']

import argparse
import os

from pywicta.denoising.inverse_transform_sampling import EmpiricalDistribution
from pywicta.denoising.rejection_criteria import CTAMarsCriteria

from pywicta.io.images import image_generator, save_benchmark_images, fill_nan_pixels

def extract_images(input_file_or_dir_path_list,
                   cam_id,
                   output_directory=None,
                   max_num_img=None,
                   tel_id=None,
                   event_id=None,
                   rejection_criteria=None,
                   noise_distribution=None,
                   export_time_slices=False):

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

        for image in image_generator(input_file_or_dir_path_list,
                                     max_num_images=max_num_img,
                                     tel_filter_list=tel_id,
                                     ev_filter_list=event_id,
                                     cam_filter_list=[cam_id],
                                     mc_rejection_criteria=rejection_criteria,
                                     ctapipe_format=False,
                                     integrator=integrator,
                                     integrator_window_width=integrator_window_width,
                                     integrator_window_shift=integrator_window_shift,
                                     integration_correction=integration_correction,
                                     mix_channels=True,
                                     time_samples=export_time_slices):

            simtel_basename = os.path.basename(image.meta['file_path'])

            # INJECT NOISE IN NAN ##################################

            # See https://stackoverflow.com/questions/29365194/replacing-missing-values-with-random-in-a-numpy-array

            if noise_distribution is not None:
                nan_mask = fill_nan_pixels(image.input_image, noise_distribution)

            if noise_distribution is not None:
                if image.input_samples is not None:
                    for sample_index in range(len(image.input_samples)):
                        # TODO: this is not the same noise distribution for timeslices!!!
                        nan_mask = fill_nan_pixels(image.input_samples[sample_index], noise_distribution)

            # SAVE THE IMAGE ##########################################

            output_file_path_template = "{}_TEL{:03d}_EV{:05d}.fits"

            if output_directory is not None:
                prefix = os.path.join(output_directory, simtel_basename)
            else:
                prefix = simtel_basename

            output_file_path = output_file_path_template.format(prefix,
                                                                image.meta["tel_id"],
                                                                image.meta["event_id"])

            print("saving", output_file_path)

            save_benchmark_images(img=image.input_image,
                                  pe_img=image.reference_image,
                                  metadata=image.meta,
                                  output_file_path=output_file_path,
                                  sample_imgs=image.input_samples)


def main():

    CAM_IDS = ("ASTRICam", "CHEC", "DigiCam", "FlashCam", "NectarCam", "LSTCam")

    # PARSE OPTIONS ###########################################################

    desc = "Generate FITS files compliant for cleaning benchmark (from simtel files)."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("--camid", metavar="STRING", 
                        help="Only process images from the specified camera: {}".format(str(CAM_IDS)))

    parser.add_argument("--max-images", type=int, metavar="INTEGER", 
                        help="The maximum number of images to export")

    parser.add_argument("--min-npe", type=float, metavar="FLOAT", default=0,
                        help="Only export images where the MC reference image has more than min-npe PE counts.")

    parser.add_argument("--max-npe", type=float, metavar="FLOAT", default=100000,
                        help="Only export images where the MC reference image has less than max-npe PE counts.")

    parser.add_argument("--min-radius", type=float, metavar="FLOAT", default=0,
                        help="Only export images where the shower Hillascentroid in the MC reference image is outside a disc of min-radius percent degrees (centered on the center of the camera).")

    parser.add_argument("--max-radius", type=float, metavar="FLOAT", default=100,
                        help="Only export images where the shower Hillascentroid in the MC reference image is inside a disc of max-radius percent degrees (centered on the center of the camera).")

    parser.add_argument("--min-ellipticity", type=float, metavar="FLOAT", default=0,
                        help="Only export images where the shower Hillas ellipsis in the MC reference image has a ratio of width over length greater than this min-ellipticity parameter.")

    parser.add_argument("--max-ellipticity", type=float, metavar="FLOAT", default=1,
                        help="Only export images where the shower Hillas ellipsis in the MC reference image has a ratio of width over length lower than this max-ellipticity parameter.")

    parser.add_argument("--telescope", "-t",
                        metavar="INTEGER LIST",
                        help="The telescopes to query (telescopes number separated by a comma)")

    parser.add_argument("--event", "-e",
                        metavar="INTEGER LIST",
                        help="The events to extract (events ID separated by a comma)")

    parser.add_argument("--time-slices", "-T", action="store_true",
                        help="Include the timeslices in the Fits files")

    parser.add_argument("--output", "-o",
                        metavar="DIRECTORY",
                        help="The output directory")

    parser.add_argument("--noise-cdf-file", metavar="FILE",
                        help="The JSON file containing the Cumulated Distribution Function of the noise model used to inject artificial noise in blank pixels (those with a NaN value). Default=None.")

    parser.add_argument("fileargs", nargs="+", metavar="FILE",
                        help="The simtel files to process")

    args = parser.parse_args()

    export_time_slices = args.time_slices
    cam_id = args.camid
    max_images = args.max_images
    max_npe = args.max_npe
    min_npe = args.min_npe
    max_radius = args.max_radius
    min_radius = args.min_radius
    max_ellipticity = args.max_ellipticity
    min_ellipticity = args.min_ellipticity

    assert min_npe <= max_npe
    assert min_radius <= max_radius
    assert min_ellipticity <= max_ellipticity

    rejection_criteria = CTAMarsCriteria(cam_id=cam_id,
                                         min_npe=min_npe,
                                         max_npe=max_npe,
                                         min_radius_meters=min_radius,
                                         max_radius_meters=max_radius,
                                         min_ellipticity=min_ellipticity,
                                         max_ellipticity=max_ellipticity)

    if args.telescope is None:
        tel_id_filter_list = None
    else:
        tel_id_filter_list = [int(tel_id_str) for tel_id_str in args.telescope.split(",")]

    if args.event is None:
        event_id_filter_list = None
    else:
        event_id_filter_list = [int(event_id_str) for event_id_str in args.event.split(",")]

    print("Telescopes:", tel_id_filter_list)
    print("Events:", event_id_filter_list)

    noise_cdf_file = args.noise_cdf_file
    if noise_cdf_file is not None:
        noise_distribution = EmpiricalDistribution(noise_cdf_file)
    else:
        noise_distribution = None

    output_directory = args.output
    input_file_or_dir_path_list = args.fileargs

    if output_directory is not None:
        if not (os.path.exists(output_directory) and os.path.isdir(output_directory)):
            raise Exception("{} does not exist or is not a directory.".format(output_directory))

    # EXTRACT AND SAVE THE IMAGES ###################################

    extract_images(input_file_or_dir_path_list,
                   cam_id=cam_id,
                   output_directory=output_directory,
                   max_num_img=max_images,
                   tel_id=tel_id_filter_list,
                   event_id=event_id_filter_list,
                   rejection_criteria=rejection_criteria,
                   noise_distribution=noise_distribution,
                   export_time_slices=export_time_slices)


if __name__ == "__main__":
    main()

