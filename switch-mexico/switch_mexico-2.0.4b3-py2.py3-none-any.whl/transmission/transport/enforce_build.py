# Copyright (c) 2015-2017 The Switch Authors. All rights reserved.
# Licensed under the Apache License, Version 2.0, which is in the LICENSE file.

"""
Defines transmission build-outs.
"""

import os
from pyomo.environ import *
from switch_model.financials import capital_recovery_factor as crf
import pandas as pd
import pdb

dependencies = 'switch_model.timescales', 'switch_model.balancing.load_zones',\
    'switch_model.financials'

def define_components(mod):
    """ Enforce build"""

    mod.TRANSMISSION_LINES = Set()
    mod.trans_lz1 = Param(mod.TRANSMISSION_LINES, within=mod.LOAD_ZONES)
    mod.trans_lz2 = Param(mod.TRANSMISSION_LINES, within=mod.LOAD_ZONES)
    mod.min_data_check('TRANSMISSION_LINES', 'trans_lz1', 'trans_lz2')
    mod.trans_dbid = Param(mod.TRANSMISSION_LINES, default=lambda m, tx: tx)
    mod.trans_length_km = Param(mod.TRANSMISSION_LINES, within=PositiveReals)
    mod.trans_efficiency = Param(
        mod.TRANSMISSION_LINES,
        within=PositiveReals,
        validate=lambda m, val, tx: val <= 1)
    mod.trans_build_year = Param(mod.TRANSMISSION_LINES, default="Legacy")
    mod.existing_trans_cap = Param(
        mod.TRANSMISSION_LINES,
        within=NonNegativeReals)

    def trans_years(model) :
        return (i for i in model.trans_build_year.items())

    mod.trans_build_years = Set(
            dimen=2,
            initialize=trans_years)

    # Read legacy and build years
    mod.BLD_YRS_FOR_EXISTING_TX = Set(
        dimen=2,
        initialize=trans_years)

    mod.min_data_check(
        'trans_length_km', 'trans_efficiency', 'BLD_YRS_FOR_EXISTING_TX',
        'existing_trans_cap')

    # All transmission lines can build by default
    mod.trans_new_build_allowed = Param(
        mod.TRANSMISSION_LINES, within=Boolean, default=True)

    mod.NEW_TRANS_BLD_YRS = Set(
        dimen=2,
        initialize=mod.TRANSMISSION_LINES * mod.PERIODS,
        filter=lambda m, tx, p: m.trans_new_build_allowed[tx])

    mod.BLD_YRS_FOR_TX = Set(
        dimen=2,
        initialize=lambda m: m.BLD_YRS_FOR_EXISTING_TX | m.NEW_TRANS_BLD_YRS)

    def tx_build_can_operate_in_period(m, tx, build_year, period):
        if build_year == "Legacy": return (0)
        if build_year in m.PERIODS:
            online = m.period_start[build_year]
        else:
            online = build_year
        retirement = online + 25
        return (
            online <= m.period_start[period] < retirement
        )

    def tx_builds_in_period(mod, period):
        vale = []
        for (tx, bld_yr) in mod.BLD_YRS_FOR_TX:
            if bld_yr == 'Legacy': continue
            if mod.period_start[period] <= bld_yr <= mod.period_end[period]:
                vale.append((tx, bld_yr))
            else:
                continue

        return vale


    mod.TX_BUILDS_IN_PERIOD = Set(
        mod.PERIODS,
        within=mod.BLD_YRS_FOR_TX,
        ordered=True,
        initialize=tx_builds_in_period)

    #  mod.TX_BUILDS_IN_PERIOD = Set(
    #      mod.PERIODS,
    #      within=mod.BLD_YRS_FOR_TX,
    #      initialize=lambda m, p: set(
    #          (tx, bld_yr) for (tx, bld_yr) in m.BLD_YRS_FOR_TX
    #          if bld_yr == 'Legacy' or bld_yr <= p))

    def bounds_BuildTx(model, tx, bld_yr):
        if((tx, bld_yr) in model.BLD_YRS_FOR_EXISTING_TX):
            return (model.existing_trans_cap[tx],
                    model.existing_trans_cap[tx])
        else:
            return (0, None)

    mod.BuildTx = Var(
        mod.BLD_YRS_FOR_TX,
        within=NonNegativeReals,
        bounds=bounds_BuildTx)

    mod.TxCapacityNameplate = Expression(
        mod.TRANSMISSION_LINES, mod.PERIODS,
        rule=lambda m, tx, period: sum(
            m.BuildTx[tx, bld_yr]
            for (tx2, bld_yr) in m.BLD_YRS_FOR_TX
            if tx2 == tx and (bld_yr == 'Legacy' or bld_yr <= period)))

    mod.trans_derating_factor = Param(
        mod.TRANSMISSION_LINES,
        within=NonNegativeReals,
        default=1,
        validate=lambda m, val, tx: val <= 1)

    mod.TxCapacityNameplateAvailable = Expression(
        mod.TRANSMISSION_LINES, mod.PERIODS,
        rule=lambda m, tx, period: (
            m.TxCapacityNameplate[tx, period] * m.trans_derating_factor[tx]))

    mod.trans_terrain_multiplier = Param(
        mod.TRANSMISSION_LINES,
        within=Reals,
        default=1,
        validate=lambda m, val, tx: val >= 0.5 and val <= 3)

    mod.trans_capital_cost_per_mw_km = Param(
        within=PositiveReals,
        default=1000)

    mod.trans_lifetime_yrs = Param(
        within=PositiveReals,
        default=20)

    mod.trans_fixed_om_fraction = Param(
        within=PositiveReals,
        default=0.03)

    # Total annual fixed costs for building new transmission lines...
    # Multiply capital costs by capital recover factor to get annual
    # payments. Add annual fixed O&M that are expressed as a fraction of
    # overnight costs.
    mod.trans_cost_annual = Param(
        mod.TRANSMISSION_LINES,
        within=PositiveReals,
        initialize=lambda m, tx: (
            m.trans_capital_cost_per_mw_km * m.trans_terrain_multiplier[tx] *
            m.trans_length_km[tx] * (crf(m.interest_rate, m.trans_lifetime_yrs) +
                m.trans_fixed_om_fraction)))
    # An expression to summarize annual costs for the objective
    # function. Units should be total annual future costs in $base_year
    # real dollars. The objective function will convert these to
    # base_year Net Present Value in $base_year real dollars.
    mod.TxFixedCosts = Expression(
        mod.PERIODS,
        rule=lambda m, p: sum(
            m.BuildTx[tx, bld_yr] * m.trans_cost_annual[tx]
            for (tx, bld_yr) in m.TX_BUILDS_IN_PERIOD[p]))
    mod.Cost_Components_Per_Period.append('TxFixedCosts')

    def init_DIRECTIONAL_TX(model):
        tx_dir = set()
        for tx in model.TRANSMISSION_LINES:
            tx_dir.add((model.trans_lz1[tx], model.trans_lz2[tx]))
            tx_dir.add((model.trans_lz2[tx], model.trans_lz1[tx]))
        return tx_dir
    mod.DIRECTIONAL_TX = Set(
        dimen=2,
        initialize=init_DIRECTIONAL_TX)
    mod.TX_CONNECTIONS_TO_ZONE = Set(
        mod.LOAD_ZONES,
        initialize=lambda m, lz: set(
            z for z in m.LOAD_ZONES if (z,lz) in m.DIRECTIONAL_TX))

    def init_trans_d_line(m, zone_from, zone_to):
        for tx in m.TRANSMISSION_LINES:
            if((m.trans_lz1[tx] == zone_from and m.trans_lz2[tx] == zone_to) or
               (m.trans_lz2[tx] == zone_from and m.trans_lz1[tx] == zone_to)):
                return tx
    mod.trans_d_line = Param(
        mod.DIRECTIONAL_TX,
        within=mod.TRANSMISSION_LINES,
        initialize=init_trans_d_line)



def load_inputs(mod, switch_data, inputs_dir):
    """
    Import data related to transmission builds. The following files are
    expected in the input directory:

    transmission_lines.tab
        TRANSMISSION_LINE, trans_lz1, trans_lz2, trans_length_km,
        trans_efficiency, existing_trans_cap

    The next files are optional. If they are not included or if any rows
    are missing, those parameters will be set to default values as
    described in documentation. If you only want to override some
    columns and not others in trans_optional_params, put a dot . in the
    columns that you don't want to override.

    trans_optional_params.tab
        TRANSMISSION_LINE, trans_dbid, trans_derating_factor,
        trans_terrain_multiplier, trans_new_build_allowed

    Note that the next file is formatted as .dat, not as .tab. The
    distribution_loss_rate parameter should only be inputted if the 
    local_td module is loaded in the simulation. If this parameter is
    specified a value in trans_params.dat and local_td is not included
    in the module list, then an error will be raised.

    trans_params.dat
        trans_capital_cost_per_mw_km, trans_lifetime_yrs,
        trans_fixed_om_fraction, distribution_loss_rate


    """

    switch_data.load_aug(
        filename=os.path.join(inputs_dir, 'transmission_lines.tab'),
        select=('TRANSMISSION_LINE', 'trans_lz1', 'trans_lz2',
                'trans_length_km', 'trans_efficiency', 'existing_trans_cap',
                'trans_build_year'),
        index=mod.TRANSMISSION_LINES,
        param=(mod.trans_lz1, mod.trans_lz2, mod.trans_length_km,
               mod.trans_efficiency, mod.existing_trans_cap,
               mod.trans_build_year))
    switch_data.load_aug(
        filename=os.path.join(inputs_dir, 'trans_optional_params.tab'),
        optional=True,
        select=('TRANSMISSION_LINE', 'trans_dbid', 'trans_derating_factor',
                'trans_terrain_multiplier', 'trans_new_build_allowed'),
        param=(mod.trans_dbid, mod.trans_derating_factor,
               mod.trans_terrain_multiplier, mod.trans_new_build_allowed))
    trans_params_path = os.path.join(inputs_dir, 'trans_params.dat')
    if os.path.isfile(trans_params_path):
        switch_data.load(filename=trans_params_path)


def post_solve(instance, outdir):
    mod = instance
    pdb.set_trace()
    normalized_dat = [
        {
            "TRANSMISSION_LINE": tx,
            "PERIOD": p,
            "trans_lz1": mod.trans_lz1[tx],
            "trans_lz2": mod.trans_lz2[tx],
            "trans_dbid": mod.trans_dbid[tx],
            "trans_length_km": mod.trans_length_km[tx],
            "trans_efficiency": mod.trans_efficiency[tx],
            "trans_derating_factor": mod.trans_derating_factor[tx],
            "TxCapacityNameplate": value(mod.TxCapacityNameplate[tx,p]),
            "TxCapacityNameplateAvailable": value(mod.TxCapacityNameplateAvailable[tx,p]),
            "TotalAnnualCost": value(mod.TxCapacityNameplate[tx,p] * mod.trans_cost_annual[tx])
        } for tx, p in mod.TRANSMISSION_LINES * mod.PERIODS
    ]
    tx_build_df = pd.DataFrame(normalized_dat)
    tx_build_df.set_index(["TRANSMISSION_LINE", "PERIOD"], inplace=True)
    tx_build_df.to_csv(os.path.join(outdir, "transmission.csv"))
