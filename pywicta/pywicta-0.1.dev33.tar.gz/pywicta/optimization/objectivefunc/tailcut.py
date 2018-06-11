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
                 pixels_clusters_filtering="off",
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
        filter_thresholds : list of float
            Thresholds used for the plane filtering.
        pixels_clusters_filtering : str
            Defines the method used to remove isolated pixels after the tail-cut image cleaning.
            Accepted values are: "off", "scipy" or "mars".

            - "off": don't apply any filtering after the tail-cut image cleaning.
            - "scipy": keep only the largest cluster of pixels after the tail-cut image cleaning.
              See :mod:`pywi.processing.filtering.pixel_clusters` for more information.
            - "mars": apply the same filtering than in CTA-Mars analysis, keep only *significant core pixels* that have
              at least two others *significant core pixels* among its neighbors (a *significant core pixels* is a pixel
              above the *core threshold*).
        cleaning_failure_score : float
            The score to attribute to images that the cleaning algorithm had failed to process.
        save_json_intermediate_results : bool
            If True, save the full result file for each solution assessed (JSON file).
        rejection_criteria: func
            The function used to define whether an image cleaning failed or not.
        """

        self.call_number = 0
        self.aggregated_score_df = None
        self.save_json_intermediate_results = save_json_intermediate_results

        self.input_files = input_files
        self.cam_id = cam_id
        self.optimization_metric = optimization_metric
        self.max_num_img = max_num_img
        self.aggregation_method = aggregation_method  # "mean" or "median"
        self.rejection_criteria = rejection_criteria

        # Init the wavelet class ################

        self.cleaning_algorithm = Tailcut()

        # Wavelet parameters ####################

        self.pixels_clusters_filtering = pixels_clusters_filtering
        self.cleaning_failure_score = cleaning_failure_score

        # PRE PROCESSING FILTERING ############################################

        # TODO...

    def __str__(self):
        """Return a string representation of the ObjectiveFunction object."""

        params_str = "tailcut"
        params_str += "_clusters-{}".format(self.pixels_clusters_filtering)
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

        try:
            high_threshold = float(filter_thresholds_list[0])
            low_threshold = float(filter_thresholds_list[1])

            if low_threshold > high_threshold:
                # To avoid useless computation, reject solutions where low threshold is greater than high threshold
                # (these solutions have the same result than the solution `low_threshold == high_threshold`)
                score = float('inf')

                return score       # TODO

            ###############################################

            if self.save_json_intermediate_results:
                output_file_path = "score_tc_optim_{}.json".format(self.call_number)

                label = "TC_{}".format(self.call_number)
                self.cleaning_algorithm.label = label
            else:
                output_file_path = None

            # Set "fixed" parameters ######################

            algo_params = {
                "pixels_clusters_filtering": self.pixels_clusters_filtering,
            }

            self.algo_params = algo_params

            # Set "free" parameters #######################

            algo_params_var = {
                "high_threshold": high_threshold,
                "low_threshold": low_threshold
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
            additional_info_label = ("call_number", "num_thresholds", "threshold_0", "threshold_1")
            df_columns = additional_info_label + all_scores_label

            all_scores_df = pd.DataFrame(columns=df_columns, index=range(self.max_num_img))
            # TODO: add the following columns: image_number, image_id (run_id, tel_id, event_id), npe

            # Fetch score for each image ##################

            for image_index, image_dict in enumerate(output_dict["io"]):

                all_scores_list = image_dict["score"]
                assert len(all_scores_list) == len(all_scores_label), "Wrong number of scores: {} instead of {}".format(len(all_scores_list), len(all_scores_label))

                all_scores_df.iloc[image_index] = (self.call_number, 2) + tuple(filter_thresholds_list) + tuple(all_scores_list)

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