"""
Copyright 2017 The Switch Authors. All rights reserved.
Licensed under the Apache License, Version 2, which is in the LICENSE file.

This module is the first attempt to enforce the construction of Solar PV
distributed geration by load zone. Still in beta version.

Use it at your own risk

TODO:
    * New method to include just one file with all the constrains
    * Write post solve function
"""

import os
import pandas as pd
import pdb
from pyomo.environ import *

def define_components(mod):
    """ Define sets, parameters and constrains"""

    # Read the periods to enforce
    mod.dg_PERIODS = Set()

    mod.dg_techs = Set(
            initialize=lambda m: set(gen for gen in m.GENERATION_PROJECTS
                if m.gen_tech[gen] == 'solarpv_distributed' # Change for specific tech
            ))

    # Read the targets to enforce
    mod.dg_min_target_capacity_mw = Param(
            mod.dg_PERIODS,
            within=NonNegativeReals,
            )

    # Make a set of the plants to enfocer building 
    mod.dg_gens = Set(
        initialize=mod.GENERATION_PROJECTS,
        filter=lambda m, g: g in m.dg_techs
        )

    mod.dg_years = Set(initialize=mod.dg_PERIODS)

    mod.dg_years_PERIOD = Set(
        initialize=mod.PERIODS & mod.dg_years
        )

    def dg_in_period(mod, period):
        value = []
        for (bld_yr, target) in mod.dg_min_target_capacity_mw.items():
            if mod.period_start[period] <= bld_yr <= mod.period_end[period]:
                value.append(target)
            else:
                continue
        return max(value)

    mod.dg_test = Param(
            mod.PERIODS,
            initialize=dg_in_period
            )
    # Calculate the capacity for all technologies per period
    # Deprecated
    #  mod.capacity_period = Expression(
    #          mod.dg_PERIODS,
    #          rule= lambda m, p: sum(m.GenCapacity[g, p]
    #                                  for g in m.GENERATION_PROJECTS) #          )

    # Calculate the capacity for dg technologies per period
    mod.dg_capacity = Expression(
            mod.dg_years_PERIOD,
            rule= lambda m, p: sum(m.GenCapacity[g, p]
                                    for g in m.dg_gens)
            )

    # Enforce the constrain
    mod.Enfoce_dg = Constraint(
            mod.dg_years_PERIOD,
            rule=lambda m, p: m.dg_capacity[p] >= m.dg_test[p]
            )

def load_inputs(mod, switch_data, inputs_dir, ext='.csv'):
    """ Load input file to DataPortal"""

    file_name = 'distributed_pv{ext}'.format(ext=ext)
    file_path = os.path.join(inputs_dir, file_name)

    switch_data.load_aug(
        filename=file_path,
        autoselect=True,
        index=mod.dg_PERIODS,
        param=(mod.dg_min_target_capacity_mw,)
        )

def post_solve(instance, outdir):
    """
    Export energy statistics relevant to RPS studies.
    """
    mod = instance
    pdb.set_trace()
#      import switch_model.reporting as reporting
#      def get_row(m, p):
#          row = (p,)
#          row += (m.RPSFuelEnergy[p] / 1000,)
#          row += (m.RPSNonFuelEnergy[p] / 1000,)
#          row += (total_generation_in_period(m,p) / 1000,)
#          row += ((m.RPSFuelEnergy[p] + m.RPSNonFuelEnergy[p]) /
#              total_generation_in_period(m,p),)
#          row += (total_demand_in_period(m, p),)
#          row += ((m.RPSFuelEnergy[p] + m.RPSNonFuelEnergy[p]) /
#              total_demand_in_period(m, p),)
#          return row
#      reporting.write_table(
#          instance, instance.RPS_PERIODS,
#          output_file=os.path.join(outdir, "rps_energy.txt"),
#          headings=("PERIOD", "RPSFuelEnergyGWh", "RPSNonFuelEnergyGWh",
#              "TotalGenerationInPeriodGWh", "RPSGenFraction",
#              "TotalSalesInPeriodGWh", "RPSSalesFraction"),
#          values=get_row)
