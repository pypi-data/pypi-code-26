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

from pywicta.denoising.wavelets_mrtransform import WaveletTransform
from pywicta.benchmark import assess

import os
import time
import shutil
import traceback
import sys

import pandas as pd

from pywi.processing.filtering import hard_filter
from pywi.processing.transform import mrtransform_wrapper

# OPTIMIZER ##################################################################

class ObjectiveFunction:

    def __init__(self,
                 input_files,
                 cam_id,
                 optimization_metric="hillas2_delta_psi_norm",
                 max_num_img=None,
                 aggregation_method="mean",
                 num_scales=None,
                 type_of_filtering=hard_filter.DEFAULT_TYPE_OF_FILTERING,
                 last_scale_treatment=mrtransform_wrapper.DEFAULT_LAST_SCALE_TREATMENT,
                 detect_only_positive_structures=False,
                 kill_isolated_pixels=False,
                 noise_distribution=None,
                 tmp_files_directory="/dev/shm/.jd/",  # TODO
                 cleaning_failure_score=90.,  # TODO
                 save_json_intermediate_results=False,
                 rejection_criteria=None):
        """The objective function used to optimize the Wavelet filtering thresholds.

        It assess the image cleaning algorithm for a given setup, a given metric and the given training set of images.

        Parameters
        ----------
        input_files : list of str
            The paths of images used for the train and test set.
        cam_id : str
            The camera Id: "ASTRICam", "CHEC", "DigiCam", "FlashCam", "NectarCam" or "LSTCam".
        optimization_metric : str
            The name of the metric used for the optimization (see `pywicta.benchmark.assess`).
        max_num_img: int
            The maximum number of images to assess.
        aggregation_method: str
            The method to use to aggregate scores from assessed images: "mean" or "median".
        num_scales: int
            The number of scales of the Wavelet transform (counting the *residual* scale
            i.e. ``num_scales - 1`` planes will be filtered).
        type_of_filtering : str
            Type of filtering: 'hard_filtering' or 'ksigma_hard_filtering'.
        filter_thresholds : list of float
            Thresholds used for the plane filtering.
        last_scale_treatment : str
            Last plane treatment: 'keep', 'drop' or 'mask'.
        detect_only_positive_structures : bool
            Detect only positive structures.
        kill_isolated_pixels : bool
            Suppress isolated pixels in the support.
        noise_distribution : bool
            The JSON file containing the Cumulated Distribution Function of the
            noise model used to inject artificial noise in blank pixels (those
            with a NaN value).
        tmp_files_directory : str
            The path of the directory where temporary files are written.
        cleaning_failure_score : float
            The score to attribute to images that the cleaning algorithm had failed to process.
        save_json_intermediate_results : bool
            If True, save the full result file for each solution assessed (JSON file).
        rejection_criteria: func
            The function used to define whether an image cleaning failed or not.
        """

        self.call_number = 0
        #self.aggregated_score_list = []
        self.aggregated_score_df = None
        self.save_json_intermediate_results = save_json_intermediate_results

        self.input_files = input_files
        self.cam_id = cam_id
        self.optimization_metric = optimization_metric
        self.max_num_img = max_num_img
        self.aggregation_method = aggregation_method  # "mean" or "median"
        self.rejection_criteria = rejection_criteria

        # Init the wavelet class ################

        self.cleaning_algorithm = WaveletTransform()

        # Wavelet parameters ####################

        if num_scales not in range(2, 8):
            raise ValueError("Wrong value for num_scales: {}. Should be in range (2, 8).".format(num_scales))

        self.num_scales = num_scales
        self.type_of_filtering = type_of_filtering
        self.last_scale_treatment = last_scale_treatment
        self.detect_only_positive_structures = detect_only_positive_structures
        self.kill_isolated_pixels = kill_isolated_pixels
        self.noise_distribution = noise_distribution
        self.cleaning_failure_score = cleaning_failure_score
        self.tmp_files_directory = tmp_files_directory

        # PRE PROCESSING FILTERING ############################################

        # TODO...

    def __str__(self):
        """Return a string representation of the ObjectiveFunction object."""

        params_str = "wavelet_mrtransform"
        params_str += "_{}-scales".format(self.num_scales)
        params_str += "_{}".format(self.type_of_filtering.replace("_", "-"))
        params_str += "_{}".format(self.last_scale_treatment.replace("_", "-"))
        params_str += "_{}".format("pos-only" if self.detect_only_positive_structures else "pos-and-neg")
        params_str += "_{}".format("kill" if self.kill_isolated_pixels else "no-kill")
        # params_str += str(self.noise_distribution)  # TODO
        params_str += "_failure-{}".format(self.cleaning_failure_score)
        params_str += "_agg-{}".format(self.aggregation_method)
        params_str += "_metric-{}".format(self.optimization_metric.lower())

        return params_str

    def __call__(self, filter_thresholds):
        """Returns the aggregated score of the tested solution (i.e. the score for `filter_thresholds`).

        This is the objective function used by the optimizer to find the best solution
        (i.e. the `filter_thresholds` that gives the minimal aggregated score).

        Parameters
        ----------
        filter_thresholds: list or array like
            The solution to assess.

        Returns
        -------
        float
            The aggregated score of the assessed solution.
        """

        self.call_number += 1

        # Convert filter_thresholds to a list object if needed (depending on the optimizer a list
        # or a numpy array can be returned)
        if isinstance(filter_thresholds, (np.ndarray, np.generic)):
            filter_thresholds_list = filter_thresholds.tolist()
        else:
            filter_thresholds_list = filter_thresholds

        # Check the length of filter_thresholds_list is consistent with self.num_scales
        if len(filter_thresholds_list) != (self.num_scales - 1):
            raise ValueError("The tested solution has a wrong number of dimensions: "
                             "{} instead of {}".format(len(filter_thresholds),
                                                       self.num_scales - 1))

        try:
            if self.save_json_intermediate_results:
                output_file_path = "score_wavelets_mrt_optim_{}.json".format(self.call_number)

                label = "WT_MRT_{}".format(self.call_number)
                self.cleaning_algorithm.label = label
            else:
                output_file_path = None

            # Make the temp file directory ################

            tmp_files_directory = "{}{}_{}".format(self.tmp_files_directory, os.getpid(), time.time())
            if not os.path.exists(tmp_files_directory):
                os.makedirs(tmp_files_directory)

            while not os.path.exists(tmp_files_directory):
                print('Waiting for the creation of', tmp_files_directory)
                time.sleep(1)

            # Set "fixed" parameters ######################

            algo_params = {
                "type_of_filtering": self.type_of_filtering,
                "last_scale_treatment": self.last_scale_treatment,
                "detect_only_positive_structures": self.detect_only_positive_structures,
                "kill_isolated_pixels": self.kill_isolated_pixels,
                "noise_distribution": self.noise_distribution,
                "tmp_files_directory": tmp_files_directory
            }

            self.algo_params = algo_params

            # Set "free" parameters #######################

            algo_params_var = {
                "filter_thresholds": filter_thresholds_list
            }

            algo_params.update(algo_params_var)

            # Assess images in the training set ###########

            output_dict = self.cleaning_algorithm.run(algo_params,
                                                      input_file_or_dir_path_list=self.input_files,
                                                      benchmark_method="all",
                                                      output_file_path=output_file_path,
                                                      max_num_img=self.max_num_img,
                                                      cam_id=self.cam_id,
                                                      rejection_criteria=self.rejection_criteria)

            # Prepare the data frame used to store results

            all_scores_label = tuple(assess.get_metrics_names(benchmark_method="all"))
            additional_info_label = ("call_number", "num_thresholds") + tuple(["threshold_{}".format(nth) for nth in range(self.num_scales - 1)])
            df_columns = additional_info_label + all_scores_label

            all_scores_df = pd.DataFrame(columns=df_columns, index=range(self.max_num_img))
            # TODO: add the following columns: image_number, image_id (run_id, tel_id, event_id), npe

            # Fetch score for each image ##################

            for image_index, image_dict in enumerate(output_dict["io"]):

                all_scores_list = image_dict["score"]
                assert len(all_scores_list) == len(all_scores_label), "Wrong number of scores: {} instead of {}".format(len(all_scores_list), len(all_scores_label))

                all_scores_df.iloc[image_index] = (self.call_number, self.num_scales) + tuple(filter_thresholds_list) + tuple(all_scores_list)

            # Aggregate scores ############################

            if self.aggregation_method == "mean":
                aggregated_all_scores_series = all_scores_df.mean(axis=0)
            elif self.aggregation_method == "median":
                aggregated_all_scores_series = all_scores_df.median(axis=0)
            else:
                raise ValueError("Unknown value for aggregation_method: {}".format(self.aggregation_method))

            print(algo_params_var, aggregated_all_scores_series, self.aggregation_method)

            #self.score_list.append(all_scores_df.iloc[0:image_index+1])   # TODO  add the call index

            if self.aggregated_score_df is None:
                self.aggregated_score_df = pd.DataFrame([aggregated_all_scores_series.values], columns=aggregated_all_scores_series.index)
            else:
                self.aggregated_score_df = self.aggregated_score_df.append(pd.DataFrame([aggregated_all_scores_series.values], columns=aggregated_all_scores_series.index),
                                                                           ignore_index=True,
                                                                           verify_integrity=True)

            # Remove the temp file directory ##############

            shutil.rmtree(tmp_files_directory)

        except Exception as e:

            print("ERROR: error with thresholds", filter_thresholds_list, "(aborted)", e)

            # The following line print the full trackback
            traceback.print_tb(e.__traceback__, file=sys.stdout)
            sys.exit(1)

        return aggregated_all_scores_series[self.optimization_metric]


if __name__ == "__main__":
    # Test...

    func = ObjectiveFunction(input_files=["~/data/grid_prod3b_north/fits/lst/gamma/lst_faint/"],
                             cam_id="LSTCam",
                             max_num_img=10)

    filter_thresholds_list = [4, 2, 1]

    score = func(filter_thresholds_list)

    print(score)