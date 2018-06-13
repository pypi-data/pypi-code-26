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
from __future__ import division, print_function
import os

import pytest

from salvus_mesher_lite.compat import mock
from salvus_mesher_lite.interface import _MESH_TYPES, _GROUPS
from salvus_mesher_lite.interface.__main__ import main as cli_main


def test_preprocessed_schema():
    """
    Tests that information is properly extracted. This does not add any
    coverage but helps avoiding stupid errors.
    """
    assert list(_MESH_TYPES.keys()) == [
        "Globe3D",
        "Globe3DSurfaceWaves",
        "SphericalChunk3D",
        "SphericalChunk3DSurfaceWaves",
        "Circular2D",
        "AxiSEM",
        "AxiSEMCartesian",
        "Cartesian2D",
        "Cartesian3D",
        "TidalLoading"]

    assert sorted(_GROUPS.keys()) == sorted([
        'advanced',
        'attenuation',
        'basic',
        'basic_sw',
        'cartesian2D',
        'cartesian2Daxisem',
        'cartesian3D',
        'chunk2D',
        'chunk3D',
        'gravity_mesh',
        'mesh_mask',
        'ocean',
        'refinement',
        'refinement3D',
        'spherical',
        'spherical2D',
        'topography',
        'basic_tl',
        'advanced_tl',
        'topography_tl',
        'spherical_tl',
        'gravity_mesh_tl'])


def test_cli_interface_no_argument_or_help(capsys):
    """
    Should all result in the same output.
    """
    # Only testing the tail - the rest if just the output from the argument
    # parser which can be expected to work.
    expected_tail = """
Available Commands:
  Globe3D                       Generate a 3D cubed sphere mesh.
  Globe3DSurfaceWaves           Generate a 3D cubed sphere mesh.
  SphericalChunk3D              Generate a single chunk 3D mesh.
  SphericalChunk3DSurfaceWaves  Generate a single chunk 3D mesh.
  Circular2D                    Generate a circular 2D mesh.
  AxiSEM                        Generate an AxiSEM mesh.
  AxiSEMCartesian               Generate a cartesian AxiSEM mesh.
  Cartesian2D                   Generate a 2D cartesian mesh.
  Cartesian3D                   Generate a 3D cartesian mesh.
  TidalLoading                  Generate a Tidal Loading Mesh.
""".lstrip("\n")

    # No params.
    cli_main(args=[])
    out, err = capsys.readouterr()
    assert out.endswith(expected_tail)
    assert err == ""

    # Two variants of printing the help.
    cli_main(args=["-h"])
    out, err = capsys.readouterr()
    assert out.endswith(expected_tail)
    assert err == ""

    # Two variants of printing the help.
    cli_main(args=["--help"])
    out, err = capsys.readouterr()
    assert out.endswith(expected_tail)
    assert err == ""


@mock.patch("salvus_mesher_lite.mesh.run_mesher.run_mesher")
def test_roundtripping_to_yaml_and_json_files(run_mesher, tmpdir):
    json_filename = os.path.join(tmpdir.strpath, "inputs.json")
    yaml_filename = os.path.join(tmpdir.strpath, "inputs.yaml")

    # 1. Run normally with non-default value.
    cli_main(args=["Cartesian2D", "--basic.period=250"])
    assert run_mesher.call_count == 1
    assert run_mesher.call_args[0][0]["basic"]["period"] == 250.0
    run_mesher.reset_mock()

    # 2. Store in JSON file.
    cli_main(args=["Cartesian2D", "--basic.period=222",
                   "--save_json=%s" % json_filename])
    # Will not be called.
    assert run_mesher.call_count == 0
    assert os.path.exists(json_filename)

    # 3. Read from JSON file.
    cli_main(args=["--input_file=%s" % json_filename])
    assert run_mesher.call_count == 1
    assert run_mesher.call_args[0][0]["basic"]["period"] == 222.0
    assert run_mesher.call_args[0][0]["mesh_type"] == "Cartesian2D"
    run_mesher.reset_mock()

    # 4. Store in YAML file.
    cli_main(args=["Cartesian2D", "--basic.period=300",
                   "--save_yaml=%s" % yaml_filename])
    # Will not be called.
    assert run_mesher.call_count == 0
    assert os.path.exists(yaml_filename)

    # 5. Read from YAML file.
    cli_main(args=["--input_file=%s" % yaml_filename])
    assert run_mesher.call_count == 1
    assert run_mesher.call_args[0][0]["basic"]["period"] == 300.0
    assert run_mesher.call_args[0][0]["mesh_type"] == "Cartesian2D"
    run_mesher.reset_mock()


@mock.patch("salvus_mesher_lite.mesh.run_mesher.run_mesher")
@pytest.mark.parametrize("mesh_type", _MESH_TYPES)
def test_roundtripping_to_yaml_and_json_files_all_mesh_types(
        run_mesher, mesh_type, tmpdir):

    # 1. To and from json.
    json_filename = os.path.join(tmpdir.strpath, "inputs.json")
    cli_main(args=[mesh_type, "--save_json=%s" % json_filename])
    assert run_mesher.call_count == 0
    run_mesher.reset_mock()
    cli_main(args=["--input_file=%s" % json_filename])
    assert run_mesher.call_count == 1
    run_mesher.reset_mock()

    # 2. To and from YAML.
    yaml_filename = os.path.join(tmpdir.strpath, "inputs.yaml")
    cli_main(args=[mesh_type, "--save_yaml=%s" % yaml_filename])
    assert run_mesher.call_count == 0
    run_mesher.reset_mock()
    cli_main(args=["--input_file=%s" % yaml_filename])
    assert run_mesher.call_count == 1


def test_negative_numbers(capsys):
    """
    Make sure negative numbers can work as arguments.
    """
    with pytest.raises(SystemExit):
        cli_main(args=["Cartesian2D", "--basic.period", "-250"])
    out, _ = capsys.readouterr()
    assert "-250.0 is less than or equal to the minimum" in out


def test_unknown_mesh_type_error_msg(capsys):
    with pytest.raises(SystemExit):
        cli_main(args=["Random"])
    out, _ = capsys.readouterr()
    assert out.startswith("Mesh type 'Random' not valid.")


@mock.patch("salvus_mesher_lite.mesh.run_mesher.run_mesher")
@pytest.mark.parametrize("mesh_type", _MESH_TYPES)
def test_parsers_for_all_mesh_types_can_be_generated(run_mesher, mesh_type):
    """
    Assures that the argument parsers for every mesh type can at least be
    generated.
    """
    cli_main(args=[mesh_type])


@mock.patch("salvus_mesher_lite.mesh.run_mesher.run_mesher")
def test_parsing_optional_arrays(run_mesher):
    cli_main(args=["Cartesian2D", "--cartesian2D.x", "2", "None"])
    assert run_mesher.call_count == 1
    assert run_mesher.call_args[0][0]["cartesian2D"]["x"] == [2, None]
    run_mesher.reset_mock()

    cli_main(args=["Cartesian2D", "--cartesian2D.x", "null", "NONE"])
    assert run_mesher.call_count == 1
    assert run_mesher.call_args[0][0]["cartesian2D"]["x"] == [None, None]
    run_mesher.reset_mock()

    cli_main(args=["Cartesian2D", "--cartesian2D.x", "4", "8.5"])
    assert run_mesher.call_count == 1
    assert run_mesher.call_args[0][0]["cartesian2D"]["x"] == [4, 8.5]
    run_mesher.reset_mock()


@mock.patch("salvus_mesher_lite.mesh.run_mesher.run_mesher")
def test_parsing_enum_arrays(run_mesher):
    cli_main(args=["Cartesian2D",
                   "--advanced.model_parameters",
                   "VP", "VS"])
    assert run_mesher.call_count == 1
    assert run_mesher.call_args[0][0]["advanced"]["model_parameters"] == \
        ["VP", "VS"]
    run_mesher.reset_mock()


def test_helpful_error_messages(capsys):
    with pytest.raises(SystemExit):
        cli_main(args=["Cartesian2D", "--advanced.model_parameters", "yY"])
    out, _ = capsys.readouterr()
    assert ("'advanced.model_parameters[0]': 'yY' is not one of ['VP', 'VS', "
            "'VSV', 'VSH', 'VPV', 'VPH', 'RHO', 'QMU', 'QKAPPA']") in out




@pytest.mark.parametrize("mesh_type", ["AxiSEM", "AxiSEMCartesian"])
def test_mesher_runs_with_default_axisem_params(tmpdir, capsys, mesh_type):
    """
    Same as above but for the free mesher version only.
    """
    filename = os.path.join(tmpdir.strpath, "out.e")
    cli_main(args=[mesh_type, "--output_filename", filename, '-q'])
    assert os.path.exists(filename)