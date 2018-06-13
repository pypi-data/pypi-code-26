#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of the lite version of the SalvusMesher package intended to
produce meshes for AxiSEM3D. If you are looking for the full version head
over to http://mondaic.com.

:copyright:
    Copyright (C) 2016-2018 Salvus Development Team <www.mondaic.com>,
                            ETH Zurich
:license:
    GNU General Public License, Version 3 [academic use only]
    (http://www.gnu.org/copyleft/gpl.html)
"""
from __future__ import absolute_import, division, print_function

import collections
import yaml

from ..interface.validate import validate_inputs

from .cartesian import run_mesher_cartesian
from .spherical import run_mesher_spherical


R_OCEAN_REF = 1.1


def run_mesher(inputs, output_filename=None, verbose=True, overwrite_file=True,
               generate_plots=False, write_mesh_to_file=True,
               mesh_processing_callback=None, **kwargs):
    """
    Convert the input parameters into a mesh.

    The job of this function is to turn the input parameters from the higher
    level interfaces into an actual mesh by calling the appropriate lower
    level functions.

    It aims to make the creation of the most common meshes as easy as possible.

    :type inputs: dict
    :param inputs: The input parameters as definied by the JSONSchema.
    :type output_filename: str
    :param output_filename: The output filename.
    :type verbose: bool
    :param verbose: Control verbosity.
    :type overwrite_file: bool
    :param overwrite_file: Overwrite files if they already exist.
    :type generate_plots: bool
    :param generate_plots: Show plots while meshing. Slow and potentially
        memory intensive and mainly useful for debugging.
    """

    if output_filename is None and write_mesh_to_file:
        raise RuntimeError('Need a filename to write mesh to file.')

    if type(inputs) in [dict, collections.OrderedDict]:
        pass

    elif type(inputs) is str:
        with open(inputs, "r") as fh:
            inputs = yaml.load(fh.read())
        validate_inputs(inputs, exit_with_pretty_error_msg=True)

    else:
        raise TypeError('inputs should be either dict ore filename')

    if inputs["mesh_type"] == 'TidalLoading':
        raise ValueError('This feature is not included in the free SalvusMesher version.')

    elif "spherical" in inputs or 'spherical2D' in inputs:
        return run_mesher_spherical(
            inputs, output_filename, verbose=verbose,
            overwrite_file=overwrite_file, generate_plots=generate_plots,
            write_mesh_to_file=write_mesh_to_file,
            mesh_processing_callback=mesh_processing_callback, **kwargs)

    elif "cartesian2D" in inputs or "cartesian3D" in inputs or \
         "cartesian2Daxisem" in inputs:
        return run_mesher_cartesian(
            inputs, output_filename, verbose=verbose,
            overwrite_file=overwrite_file, generate_plots=generate_plots,
            write_mesh_to_file=write_mesh_to_file,
            mesh_processing_callback=mesh_processing_callback, **kwargs)

    else:
        raise NotImplementedError