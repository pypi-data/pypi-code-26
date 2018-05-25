"""
Create a list of samples in a specified folder as input for the demand sensitivity analysis.

This script creates:

- a samples folder with the files `samples.npy` and `problem.pickle` to be used by the scripts
  `sensitivity_demand_count.py`, `sensitivity_demand_simulate.py` and `sensitivity_demand_analyze.py`.

The file `samples.npy` is a NumPy array of samples to simulate, as generated by either the morris or the sobol sampler.
Each sample is a a row in the array and each row consists of a list of parameter values to use for the simulation.
The parameters correspond to the parameter names defined by the `variable_groups` input. `variable_groups` refers
to worksheets in the uncertainty db, an Excel file in `cea/databases/CH/Uncertainty/uncertainty_distributions.xls`,
which specifies row-by-row the variables to sample and their distribution parameters.

The file `problem.pickle` is a python dictionary that is saved using the standard `pickle` module and contains the
following data:

- num_vars: int, the number of variables being analyzed.
- names: list of str, the variable names in the same order as the values in each sample row. Used to apply the sample
         values to the input data using the override mechanism. See:
         - `cea.analysis.sensitivity.sensitivity_demand_simulate.apply_sample_parameters` (write overrides)
         - `cea.demand.thermal_loads.BuildingProperties#__init__` (read overrides)
- bounds: list of tuple(min, max), lower and upper bounds for each variable to sample (only used by the sampler)
- groups: None (currently not used)
"""
import os

import numpy as np
import pandas as pd
import pickle
from SALib.sample.saltelli import sample as sampler_sobol
from SALib.sample.morris import sample as sampler_morris
from cea.inputlocator import InputLocator
import cea.config

__author__ = "Jimeno A. Fonseca; Daren Thomas"
__copyright__ = "Copyright 2016, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Jimeno A. Fonseca", "Daren Thomas"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "cea@arch.ethz.ch"
__status__ = "Production"


def create_demand_samples(method='morris', num_samples=1000, variable_groups=('ENVELOPE',), sampler_parameters={}):
    """
    Create the samples to simulate using the specified method (`method`), the sampling method parameter N
    (`num_samples`) and any additional sampling method-specific parameters specified in `sampler_parameters for each
    variable definined in the uncertainty database worksheets referenced in `variable_groups`.

    :param method: The method to use. Valid values are 'morris' (default) and 'sobol'.
    :type method: str
    :param num_samples: The parameter `N` for the sampling methods (sobol defines this as "The number of samples to
                        generate", but in reality, for both methods, the actual number of samples is a multiple of
                        `num_samples`).
    :type num_samples: int
    :param sampler_parameters: additional, sampler-specific parameters. For `method='morris'` these are: [grid_jump,
                               num_levels], for `method='sobol'` these are: [calc_second_order]
    :type sampler_parameters: dict of (str, _)
    :param variable_groups: list of names of groups of variables to analyse. Possible values are:
        'THERMAL', 'ARCHITECTURE', 'INDOOR_COMFORT', 'INTERNAL_LOADS'. This list links to the probability density
        functions of the variables contained in locator.get_uncertainty_db() and refers to the Excel worksheet names.

    :return: (samples, problem) - samples is a list of configurations for each simulation to run, a configuration being
        a list of values for each variable in the problem. The problem is a dictionary with the keys 'num_vars',
        'names' and 'bounds' and describes the variables being sampled: 'names' is list of variable names of length
        'num_vars' and 'bounds' is a list of tuples(lower-bound, upper-bound) for each of these variables. Further,
        the keys 'N' (`num_samples`) and 'method' (`method`) are set and the sampler_parameters are also added to
        `problem`.
    """
    locator = InputLocator(None)

    # get probability density functions (pdf) of all variable_groups from the uncertainty database
    pdf = pd.concat([pd.read_excel(locator.get_uncertainty_db(), group, axis=1) for group in variable_groups])
    # a list of tupples containing the lower-bound and upper-bound of each variable
    bounds = list(zip(pdf['min'], pdf['max']))

    # define the problem
    problem = {'num_vars': pdf.name.count(), 'names': pdf.name.values, 'bounds': bounds, 'groups': None,
               'N': num_samples, 'method': method}
    problem.update(sampler_parameters)

    return sampler(method, problem, num_samples, sampler_parameters), problem


def sampler(method, problem, num_samples, sampler_parameters):
    """
    Run the sampler specified by `method` and return the results.

    :param method: The method to use. Valid values: 'morris', 'sobol'
    :type method: str

    :param problem: The problem dictionary as required by the sampling methods.
    :type problem: dict of (str, _)

    :param num_samples: The parameter `N` to the sampler methods of sobol and morris. NOTE: This is not the
                        the number of samples produced, but relates to the total number of samples produced in
                        a manner dependent on the sampler method used. See the documentation of sobol and morris in
                        the SALib for more information.
    :type num_samples: int

    :param sampler_parameters: Sampler method-specific parameters to be passed to the sampler function as keyword
                               arguments.
    :type sampler_parameters: dict of (str, _)

    :return: The list of samples generated as a NumPy array with one row per sample and each row containing one
             value for each variable name in `problem['names']`.
    :rtype: ndarray
    """
    if method == 'sobol':
        return sampler_sobol(problem, N=num_samples, **sampler_parameters)
    elif method == 'morris':
        return sampler_morris(problem, N=num_samples, **sampler_parameters)
    else:
        raise ValueError("Sampler method unknown: %s" % method)


def main(config):
    scenario = config.scenario
    method = config.sensitivity_demand.method
    num_samples = config.sensitivity_demand.num_samples
    calc_second_order = config.sensitivity_demand.calc_second_order
    grid_jump = config.sensitivity_demand.grid_jump
    num_levels = config.sensitivity_demand.num_levels
    samples_folder = config.sensitivity_demand.samples_folder
    variable_groups = config.sensitivity_demand.variable_groups

    assert os.path.exists(scenario), 'Scenario not found: %s' % scenario

    print("Running sensitivity-demand-samples for scenario = %s" % scenario)
    print("Running sensitivity-demand-samples with method = %s" % method)
    print("Running sensitivity-demand-samples with num-samples = %s" % num_samples)
    print("Running sensitivity-demand-samples with calc-second-order = %s" % calc_second_order)
    print("Running sensitivity-demand-samples with grid-jump = %s" % grid_jump)
    print("Running sensitivity-demand-samples with num-levels = %s" % num_levels)
    print("Running sensitivity-demand-samples with samples-folder = %s" % samples_folder)
    print("Running sensitivity-demand-samples with variable-groups = %s" % variable_groups)

    sampler_parameters = {}
    if method == 'morris':
        sampler_parameters['grid_jump'] = grid_jump
        sampler_parameters['num_levels'] = num_levels
    else:
        sampler_parameters['calc_second_order'] = calc_second_order

    samples, problem_dict = create_demand_samples(method=method,
                                                  num_samples=num_samples,
                                                  variable_groups=variable_groups,
                                                  sampler_parameters=sampler_parameters)

    # save `samples.npy` and `problem.pickle` to the samples folder
    if not os.path.exists(samples_folder):
        os.makedirs(samples_folder)
    np.save(os.path.join(samples_folder, 'samples.npy'), samples)
    with open(os.path.join(samples_folder, 'problem.pickle'), 'w') as f:
        pickle.dump(problem_dict, f)
    print('created %i samples in %s' % (samples.shape[0], samples_folder))


if __name__ == '__main__':
    main(cea.config.Configuration())
