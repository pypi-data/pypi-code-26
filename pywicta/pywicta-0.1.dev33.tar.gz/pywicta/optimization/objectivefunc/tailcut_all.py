#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Jérémie DECOCK (http://www.jdhp.org)

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

__all__ = ['ObjectiveFunction']

import numpy as np

from pywicta.denoising.tailcut import Tailcut
from pywicta.benchmark import assess
from pywicta.benchmark.assess import norm_angle_diff

import traceback
import sys


# OPTIMIZER ##################################################################

class ObjectiveFunction:

    def __init__(self,
                 input_files,
                 cam_id,
                 max_num_img=None,
                 aggregation_method="mean",
                 kill_isolated_pixels=False,
                 cleaning_failure_score=90.):

        self.call_number = 0

        # Init the wavelet class
        self.cleaning_algorithm = Tailcut()

        # Make the image list
        self.input_files = input_files
        self.max_num_img = max_num_img

        self.cam_id = cam_id

        self.aggregation_method = aggregation_method  # "mean" or "median"

        self.kill_isolated_pixels = kill_isolated_pixels

        self.cleaning_failure_score = cleaning_failure_score

        print("aggregation method:", self.aggregation_method)

        self.aggregated_score_list = []

        # PRE PROCESSING FILTERING ############################################

        # TODO...


    def __call__(self, threshold_list):
        self.call_number += 1

        aggregated_scores = []

        try:
            high_threshold = float(threshold_list[0])
            low_threshold = float(threshold_list[1])

            if low_threshold > high_threshold:
                # To avoid useless computation, reject solutions where low threshold is greater than high threshold
                # (these solutions have the same result than the solution `low_threshold == high_threshold`)
                score = float('inf')
                #score = float('nan')
                self.aggregated_score_list.append(score)
                return score       # TODO

            #low_threshold = min(low_threshold, high_threshold)  # low threshold should not be greater than high threshold

            algo_params_var = {
                        "high_threshold": high_threshold,
                        "low_threshold": low_threshold
                    }

            benchmark_method = "all"          # TODO

            label = "TC_{}".format(self.call_number)
            self.cleaning_algorithm.label = label

            #output_file_path = "score_tailcut_optim_{}.json".format(self.call_number)
            output_file_path = None

            algo_params = {
                        "kill_isolated_pixels": self.kill_isolated_pixels,
                        "verbose": False
                    }

            algo_params.update(algo_params_var)

            # TODO: randomly make a subset fo self.input_files
            input_files = self.input_files

            #rejection_criteria = lambda image: not 50 < np.nansum(image.reference_image) < 200

            output_dict = self.cleaning_algorithm.run(algo_params,
                                                      input_file_or_dir_path_list=input_files,
                                                      benchmark_method=benchmark_method,
                                                      output_file_path=output_file_path,
                                                      max_num_img=self.max_num_img,
                                                      cam_id=self.cam_id)
                                                      #rejection_criteria=rejection_criteria)

            score_list = []

            # Read and compute results from output_dict
            for image_dict in output_dict["io"]:

                # POST PROCESSING FILTERING #######################################

                # >>>TODO<<<: Filter images: decide wether the image should be used or not ? (contained vs not contained)
                # TODO: filter these images *before* cleaning them to avoid waste of computation...

                # >>>TODO<<<: Filter images by energy range: decide wether the image should be used or not ?
                # TODO: filter these images *before* cleaning them to avoid waste of computation...

                ###################################################################

                # GET THE CLEANED IMAGE SCORE

                if "score" in image_dict:
                    scores = [score for score in image_dict["score"]]
                else:
                    # The cleaning algorithm failed to clean this image
                    # TODO: add a penalty
                    NUM_METRICS = 33
                    scores = [float('nan') for score in range(NUM_METRICS)]      # TODO: AVOID THIS HARD CODED VALUE !!!
                    scores[-1] = 1.                                              # TODO: dirty workaround (the last metric is supposed to be the 'cleaning_failure_metrics')

                # WORKAROUND

                if ("img_ref_hillas_2_psi" in image_dict) and ("img_cleaned_hillas_2_psi" in image_dict):
                    output_image_parameter_psi_rad = image_dict["img_ref_hillas_2_psi"]
                    reference_image_parameter_psi_rad = image_dict["img_cleaned_hillas_2_psi"]
                    delta_psi_rad = reference_image_parameter_psi_rad - output_image_parameter_psi_rad
                    normalized_delta_psi_deg = norm_angle_diff(np.degrees(delta_psi_rad))

                    #if image_dict["score_name"][0] != "delta_psi":
                    #    raise Exception("Cannot get the score")
                    #normalized_delta_psi_deg = image_dict["score"][0]

                    scores.append(normalized_delta_psi_deg)
                else:
                    # The cleaning algorithm failed to clean this image
                    # TODO: add a penalty
                    scores.append(self.cleaning_failure_score)  # the worst score

                score_list.append(scores)

            score_array = np.array(score_list)

            assert score_array.dtype != np.object, "ERROR: score_list contain rows of different size"

            # Compute the mean
            if self.aggregation_method == "mean":
                aggregated_scores = np.nanmean(score_array, axis=0)
            elif self.aggregation_method == "median":
                aggregated_scores = np.nanmedian(score_array, axis=0)
            else:
                raise ValueError("Unknown value for aggregation_method: {}".format(self.aggregation_method))

            # TODO: save results in a JSON file (?)
            print(algo_params_var, aggregated_scores, self.aggregation_method)
        except Exception as e:
            print("ERROR: error with thresholds", threshold_list, "(aborted)", e)
            # The following line print the full trackback
            traceback.print_tb(e.__traceback__, file=sys.stdout)
            sys.exit(1)

        self.aggregated_score_list.append([float(score) for score in aggregated_scores])

        try:
            aggregated_score = float(aggregated_scores[-1])    # TODO: use name instead of index...
        except:
            aggregated_score = float('nan')                    # TODO: use name instead of index...

        return aggregated_score


if __name__ == "__main__":
    # Test...

    #func = ObjectiveFunction(input_files=["./MISC/testset/gamma/digicam/"])
    func = ObjectiveFunction(input_files=["/dev/shm/.jd/digicam/gamma/"])

    threshold_list = [10, 5]

    score = func(threshold_list)

