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

__all__ = []

import math
import numpy as np

import json
from pywicta.optimization.objectivefunc.wavelets_mrfilter import ObjectiveFunction as WaveletMRFObjectiveFunction
from pywicta.optimization.objectivefunc.wavelets_mrtransform import ObjectiveFunction as WaveletMRTObjectiveFunction
from pywicta.optimization.objectivefunc.tailcut import ObjectiveFunction as TailcutObjectiveFunction

# For wavelets
import pywicta.denoising.cdf
from pywicta.denoising.inverse_transform_sampling import EmpiricalDistribution

def main():

    #algo = "wavelet_mrfilter"
    algo = "wavelet_mrtransform"
    #algo = "tailcut"

    #instrument = "ASTRICam"
    #instrument = "CHEC"
    #instrument = "DigiCam"
    #instrument = "FlashCam"
    #instrument = "NectarCam"
    instrument = "LSTCam"

    #max_num_img = None
    max_num_img = 1000

    aggregation_method = "mean"
    #aggregation_method = "median"

    kill_islands = False

    print("algo:", algo)
    print("instrument:", instrument)
    print("kill_islands:", kill_islands)

    if instrument == "ASTRICam":

        input_files = ["/dev/shm/.jd/astri/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.ASTRI_CDF_FILE)

        if algo == "wavelet_mrfilter":
            init_min_val = np.array([0., 0., 0.])  # TODO
            init_max_val = np.array([5., 5., 5.])  # TODO
        elif algo == "wavelet_mrtransform":
            init_min_val = np.array([0., 0., 0.])  # TODO
            init_max_val = np.array([5., 5., 5.])  # TODO
        elif algo == "tailcut":
            init_min_val = np.array([1., 1.])    # TODO
            init_max_val = np.array([15., 15.])  # TODO

    elif instrument == "CHEC":

        input_files = ["/dev/shm/.jd/gct/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.GCT_CDF_FILE)

        if algo == "wavelet_mrfilter":
            init_min_val = np.array([-3., -4., -3.])
            init_max_val = np.array([10., 8., 7.])
        elif algo == "wavelet_mrtransform":
            init_min_val = np.array([0., 0., 0.])  # TODO
            init_max_val = np.array([5., 5., 5.])  # TODO
        elif algo == "tailcut":
            init_min_val = np.array([1., 1.])    # TODO
            init_max_val = np.array([15., 15.])  # TODO

    elif instrument == "DigiCam":

        input_files = ["/dev/shm/.jd/digicam/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.DIGICAM_CDF_FILE)

        if algo == "wavelet_mrfilter":
            init_min_val = np.array([-3., -4., -3.])
            init_max_val = np.array([10., 8., 7.])
        elif algo == "wavelet_mrtransform":
            init_min_val = np.array([0., 0., 0.])  # TODO
            init_max_val = np.array([5., 5., 5.])  # TODO
        elif algo == "tailcut":
            init_min_val = np.array([1., 1.])    # TODO
            init_max_val = np.array([15., 15.])  # TODO

    elif instrument == "FlashCam":

        input_files = ["/dev/shm/.jd/flashcam/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.FLASHCAM_CDF_FILE)

        if algo == "wavelet_mrfilter":
            init_min_val = np.array([0., 0., 0.])  # TODO
            init_max_val = np.array([5., 5., 5.])  # TODO
        elif algo == "wavelet_mrtransform":
            init_min_val = np.array([0., 0., 0.])  # TODO
            init_max_val = np.array([5., 5., 5.])  # TODO
        elif algo == "tailcut":
            init_min_val = np.array([1., 1.])    # TODO
            init_max_val = np.array([15., 15.])  # TODO

    elif instrument == "NectarCam":

        input_files = ["/dev/shm/.jd/nectarcam/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.NECTARCAM_CDF_FILE)

        if algo == "wavelet_mrfilter":
            init_min_val = np.array([-4., -4., -4.])
            init_max_val = np.array([16., 10., 8.])
        elif algo == "wavelet_mrtransform":
            init_min_val = np.array([0., 0., 0.])  # TODO
            init_max_val = np.array([5., 5., 5.])  # TODO
        elif algo == "tailcut":
            init_min_val = np.array([1., 1.])    # TODO
            init_max_val = np.array([15., 15.])  # TODO

    elif instrument == "LSTCam":

        input_files = ["/dev/shm/.jd/lstcam/gamma/lst_faint/"]
        #input_files = ["~/data/grid_prod3b_north/simtel/gamma"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.LSTCAM_CDF_FILE)

        if algo == "wavelet_mrfilter":
            init_min_val = np.array([1., 1., 1.])
            init_max_val = np.array([14., 9., 6.])
        elif algo == "wavelet_mrtransform":
            init_min_val = np.array([0.,  0.])
            init_max_val = np.array([15., 2.])
        elif algo == "tailcut":
            init_min_val = np.array([1., 1.])
            init_max_val = np.array([12., 12.])

    else:

        raise Exception("Unknown instrument", instrument)

    print("input_files:", input_files)
    print("noise_distribution:", noise_distribution.cdf_json_file_path)

    if algo == "wavelet_mrfilter":

        func = WaveletMRFObjectiveFunction(input_files=input_files,
                                           cam_id=instrument,
                                           noise_distribution=noise_distribution,
                                           max_num_img=max_num_img,
                                           aggregation_method=aggregation_method,  # "mean" or "median"
                                           kill_isolated_pixels=kill_islands)

    elif algo == "wavelet_mrtransform":

        func = WaveletMRTObjectiveFunction(input_files=input_files,
                                           cam_id=instrument,
                                           noise_distribution=noise_distribution,
                                           max_num_img=max_num_img,
                                           aggregation_method=aggregation_method,  # "mean" or "median"
                                           kill_isolated_pixels=kill_islands)

    elif algo == "tailcut":

        func = TailcutObjectiveFunction(input_files=input_files,
                                        cam_id=instrument,
                                        max_num_img=max_num_img,
                                        aggregation_method=aggregation_method,  # "mean" or "median"
                                        kill_isolated_pixels=kill_islands)

    else:

        raise ValueError("Unknown algorithm", algo)


    pop_list = []

    def callback(pop):
        print(pop)
        pop_list.append(pop)
        with open("optimize_sigma_saes_iterations.json", "w") as fd:
            json.dump(pop_list, fd, sort_keys=True, indent=4)  # pretty print format

    res = minimize(func,
                   init_min_val=init_min_val,
                   init_max_val=init_max_val,
                   num_gen=20,
                   mu=3,
                   lmb=6,
                   callback=callback)

    print("x* =", res['x'])
    print("f(x*) =", res['fun'])
    print("Number of evaluations of the objective functions:", res['nfev'])
    print("Number of iterations performed by the optimizer:", res['nit'])

    # SAVE RESULTS ############################################################

    with open("optimize_sigma_saes.json", "w") as fd:
        json.dump(res, fd, sort_keys=True, indent=4)  # pretty print format


def minimize(objective_function,
             init_min_val,
             init_max_val,
             num_gen=50,
             mu=3,
             lmb=6,
             callback=None):

    d = len(init_min_val)
    tau = 1./math.sqrt(2.*d)         # self-adaptation learning rate

    # Init the population ##########################

    # "pop" array layout:
    # - the first mu lines contain parents
    # - the next lambda lines contain children
    # - the first column contains the individual's strategy (sigma)
    # - the last column contains the individual's assess (f(x))
    # - the other columns contain the individual value (x)

    pop = np.full([mu+lmb, d+2], np.nan)
    pop[:mu, 0] = 1.                                       # init the parents strategy to 1.0
    #pop[:mu, 1:-1] = np.random.multivariate_normal(mean=init_pop_mu,
    #                                               cov=np.diag(init_pop_sigma**2),
    #                                               size=[mu,d])         # init the parents value
    pop[:mu, 1:-1] = np.array([np.random.uniform(min_, max_, size=mu)
                               for min_, max_
                               in zip(init_min_val, init_max_val)]).T    # init the parents value
    for parent_index in range(mu):
        pop[parent_index, -1] = objective_function(pop[parent_index, 1:-1].tolist())    # evaluate parents

    if callback is not None:
        callback(pop.tolist())

    for gen in range(num_gen):
        # Make children ################################
        pop[mu:,:] = pop[np.random.randint(mu, size=lmb)]
        pop[mu:,-1] = np.nan

        # Mutate children's sigma ######################
        pop[mu:,0] = pop[mu:,0] * np.exp(tau * np.random.normal(size=lmb))

        # Mutate children's value ######################
        pop[mu:,1:-1] = pop[mu:,1:-1] + pop[mu:,1:-1] * np.random.normal(size=[lmb,d])

        # Evaluate children ############################
        for child_index in range(lmb):
            pop[mu+child_index, -1] = objective_function(pop[mu+child_index, 1:-1].tolist())

        # Select the best individuals ##################
        pop = pop[pop[:,-1].argsort()]

        if callback is not None:
            callback(pop.tolist())

        pop[mu:, :] = np.nan

    res = {}
    res['sigma'] = pop[:mu,0].tolist()
    res['x'] =     pop[:mu,1:-1].tolist()
    res['fun'] =   pop[:mu,-1].tolist()
    res['nit'] = gen + 1
    res['nfev'] = res['nit'] * lmb + mu
    res['parent_pop'] = pop[:mu,:].tolist()
    res['init_min_val'] = init_min_val.tolist()
    res['init_max_val'] = init_max_val.tolist()
    res['num_gen'] = num_gen
    res['mu'] = mu
    res['lambda'] = lmb

    return res


if __name__ == "__main__":
    main()

