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
from __future__ import absolute_import, unicode_literals

import argparse
import collections
import copy
import io
import itertools
import json
import os
import textwrap
import sys
import yaml

from ..compat import PY2
from ..mesh import run_mesher
from . import _CMD, _GROUPS, _MESH_TYPES
from .validate import validate_inputs


# Those are arguments that do not change the actual mesh and thus are not
# part of the input parameters. They need to be handled explicitly a
# couple of times and thus we just define them once here. kwargs are passed
# on to the .add_argument() method of the ArgumentParser object.
__steering_arguments = {
    "output_filename": {"short_name": "o",
                        "kwargs": {
                            "type": str,
                            "default": "$mesh_type$_$model_name$_$period$.e",
                            "help": "Output filename for the mesh."}
                        },
    "quiet": {"short_name": "q",
              "kwargs": {
                 "action": "store_true",
                 "default": False,
                 "help": "Silence output."}},
    "overwrite_file": {"kwargs": {
                       "action": "store_true",
                       "default": False,
                       "help": "Overwrite mesh file if it exists."}},
    "generate_plots": {"kwargs": {
                       "action": "store_true",
                       "default": False,
                       "help": "Show plots while meshing. WARNING: slow and "
                       "memory intensive for short periods. In 3D only "
                       "useful for very small meshes."}}}
# Additional steering arguments used for saving to input files.
__steering_arguments_input_files_save = {
    "save_yaml": {"kwargs": {
        "type": str,
        "metavar": "FILENAME",
        "help": "If given, the mesher will not be run, but the "
                "chosen parameters will be written to a yaml "
                "file."}
    },
    "save_json": {"kwargs": {
        "type": str,
        "metavar": "FILENAME",
        "help": "If given, the mesher will not be run, but the "
                "chosen parameters will be written to a JSON "
                "file."}}}
# Additional steering arguments used for reading from input files.
__steering_arguments_input_files_retrieve = {
    "input_file": {"kwargs": {
        "type": str,
        "metavar": "FILENAME",
        "help": "Use a YAML or JSON file as an input."
    }}}


def __add_steering_args_to_parser(parser, save_inputs):
    """
    Add steering parameters to an existing argparse ArgumentParser instance.

    :param parser: The parser object to save to.
    :type save_inputs: bool
    :param save_inputs: If True, the arguments to save to an input file will be
        added, otherwise those to retrieve will be added.
    :return:
    """
    if save_inputs:
        iterargs = itertools.chain(
            __steering_arguments.items(),
            __steering_arguments_input_files_save.items())
    else:
        iterargs = itertools.chain(
            __steering_arguments.items(),
            __steering_arguments_input_files_retrieve.items())

    for name, props in iterargs:
        _args = ["--" + name]
        if "short_name" in props:
            _args.append("-" + props["short_name"])
        parser.add_argument(*_args, **props["kwargs"])


def _generate_argument_parser(mesh_type):
    """
    Dynamically generate a argument parser for the given mesh type.

    Essentially generates a seperate argument parser for each subcommand.

    :type mesh_type: str
    :param mesh_type: The chosen high-level mesh type.
    """
    mt = _MESH_TYPES[mesh_type]

    # Dynamically build up the parser.
    parser = argparse.ArgumentParser(
        prog=_CMD + " " + mesh_type,
        description=mt["description"])

    # Add the steering arguments.
    __add_steering_args_to_parser(parser, save_inputs=True)

    # Autogenerate the rest from the schema file.
    for name in mt["all_groups"]:
        g = _GROUPS[name]
        arg_group = parser.add_argument_group(g["title"], g["description"])

        for arg_name, arg_meta in g["arguments"].items():
            metavar = ""
            nargs = None
            action = None
            a_type = None

            # Resolve the type to an argparse compatible one.
            if arg_meta["type"] == "string":
                a_type = str
            elif arg_meta["type"] == "boolean":
                a_type = bool
            elif arg_meta["type"] == "integer":
                a_type = int
            elif arg_meta["type"] == "number":
                a_type = float
            elif arg_meta["type"] == "array":
                # Set nargs if appropriate.
                nargs = "+"
                if "minItems" in arg_meta and "maxItems" in arg_meta:
                    if arg_meta["minItems"] == arg_meta["maxItems"]:
                        nargs = arg_meta["minItems"]

                if "type" in arg_meta["items"] and \
                        arg_meta["items"]["type"] == "string":
                    a_type = str
                # Arrays with same type.
                elif "type" in arg_meta["items"]:
                    if arg_meta["items"]["type"] == "number":
                        a_type = float
                    else:  # pragma: no cover
                        raise NotImplementedError
                # Arrays with varying type.
                elif "anyOf" in arg_meta["items"]:
                    # Only treat the simple case for now.
                    t = [_i["type"] for _i in arg_meta["items"]["anyOf"]]

                    class OptionalType(argparse.Action):
                        def __call__(self, parser, namespace, values,
                                     option_string=None):
                            try:
                                ll = []
                                for value in values:
                                    if "null" in t and \
                                            value.lower() in ["null", "none"]:
                                        ll.append(None)
                                        continue
                                    if "number" in t:
                                        ll.append(float(value))
                            except Exception as e:  # pragma: no cover
                                parser.error(str(e))
                            setattr(namespace, self.dest, ll)

                    action = OptionalType
                else:  # pragma: no cover
                    raise NotImplementedError
            else:  # pragma: no cover
                raise NotImplementedError

            arg_group.add_argument(
                "--%s.%s" % (name, arg_name), type=a_type,
                default=arg_meta["default"], nargs=nargs,
                action=action,
                help=arg_meta["description"] +
                " (default: %s)" % str(arg_meta["default"]),
                metavar=metavar)

    return parser


def inputs_to_yaml(inputs, output_filename):
    """
    Convert the inputs dictionary to a YAML file.

    Assume inputs has been validated and everything is in the correct
    order.

    :type inputs: dict
    :param inputs: The input dictionary,
    :type output_filename: str
    :param output_filename: The output filename.
    """
    # Manually create a YAML file - much easier then forcing comments into
    # an existing YAML writer.
    yaml = "\n".join([
        "# {}".format(_MESH_TYPES[inputs["mesh_type"]]["description"]),
        "mesh_type: {}\n\n".format(inputs["mesh_type"])
    ])

    for key, value in inputs.items():
        if key == "mesh_type":
            continue

        yaml += "# {}\n".format(_GROUPS[key]["description"])
        yaml += "{}:\n".format(key)
        for k, v in value.items():
            _meta = _GROUPS[key]["arguments"][k]
            indent = "    # "
            help = _meta["description"]
            if "enum" in _meta:
                help += " Choices: [%s]" % (", ".join(_meta["enum"]))
            yaml += "\n".join(textwrap.wrap(help, initial_indent=indent,
                                            subsequent_indent=indent))
            yaml += "\n"
            if isinstance(v, str):
                yaml += '    {}: "{}"\n'.format(k, v)
            else:
                yaml += "    {}: {}\n".format(
                    k, str(v).replace("None", "null"))
            yaml += "\n"

        yaml += "\n"

    with io.open(output_filename, "w") as fh:
        fh.write(yaml)


def invoke_subcommand(mesh_type, args):
    """
    Invoke subcommand for the given mesh type,

    :tyoe mesh_type: str
    :param mesh_type: The mesh type for which to invoke the command.
    :type args: list
    :param args: Additional arguments.
    """
    # Operate on copies to not modify the original items.
    _m_types = copy.deepcopy(_MESH_TYPES)
    _g = copy.deepcopy(_GROUPS)

    if mesh_type not in _m_types:
        print("Mesh type '%s' not valid. Available mesh types: %s" % (
            mesh_type, ", ".join(_m_types.keys())))
        sys.exit(1)

    parser = _generate_argument_parser(mesh_type=mesh_type)

    args = parser.parse_args(args=args)

    inputs = collections.OrderedDict()
    inputs["mesh_type"] = mesh_type

    for g in _m_types[mesh_type]["all_groups"]:
        inputs[g] = collections.OrderedDict()

    for key, value in args._get_kwargs():
        # Skip steering arguments.
        if key in __steering_arguments or \
                key in __steering_arguments_input_files_save:
            continue
        group_name, key = key.split('.')
        inputs[group_name][key] = value

    # Make sure its sorted to produce more consistent YAML and JSON files
    # later down the road.
    for key, value in inputs.items():
        # Skip mesh_type key - its already good.
        if key == "mesh_type":
            continue
        new_value = collections.OrderedDict()
        for k in list(_g[key]["arguments"].keys()):
            new_value[k] = value[k]
        inputs[key] = new_value

    return inputs, args


def print_help():
    """
    Print the help message of the CLI interface.
    """
    parser = argparse.ArgumentParser(
        prog=_CMD,
        description="CLI interface for the Salvus mesher.")
    __add_steering_args_to_parser(parser, save_inputs=False)
    parser.print_help()

    fmt_str = "{:<%i}" % max(len(_i) for _i in _MESH_TYPES)
    print("")
    print("Available Commands:")
    for key, value in _MESH_TYPES.items():
        print("  " + fmt_str.format(key) + "  " + value["description"])


def main(args=sys.argv[1:]):
    """
    Main entry point for the CLI interface.

    :type args: list
    :param args: The command line parameters.
    """
    # handle negative digits in the arguments which could be misinterpreted as
    # options otherwise. See http://stackoverflow.com/a/21446783
    for i, arg in enumerate(args):
        if (arg[0] == '-') and arg[1].isdigit():
            args[i] = ' ' + arg

    # Show root level help if desired.
    if not args or args in [["--help"], ["-h"]]:
        print_help()
        return

    # This branch is executed if an input file is passed.
    if [_i for _i in args if _i.strip().startswith("--input_file")]:
        parser = argparse.ArgumentParser()
        __add_steering_args_to_parser(parser, save_inputs=False)
        parsed_args = parser.parse_args(args=args)
        assert os.path.exists(parsed_args.input_file), \
            "The input files must exist."

        # This interestingly enough also works for JSON files.
        with open(parsed_args.input_file, "r") as fh:
            inputs = yaml.load(fh.read())

    # This branch is run if arguments are passed.
    else:
        # Parse everything to a common dictionary.
        inputs, parsed_args = \
            invoke_subcommand(mesh_type=args[0], args=args[1:])

    # Validate everything.
    validate_inputs(inputs, exit_with_pretty_error_msg=True)

    # Save to files if either of the two is given.
    if hasattr(parsed_args, "save_yaml") and \
            (parsed_args.save_yaml or parsed_args.save_json):
        if parsed_args.save_yaml:
            inputs_to_yaml(inputs, parsed_args.save_yaml)
            print("Saved arguments to '%s'. The mesher itself did not run." %
                  parsed_args.save_yaml)
        if parsed_args.save_json:
            with io.open(parsed_args.save_json,
                         mode="wb" if PY2 else "wt") as fh:
                json.dump(inputs, fh, indent=4)
            print("Saved arguments to '%s'. The mesher itself did not run." %
                  parsed_args.save_json)
        return

    # Run mesher and also pass the steering parameters.
    run_mesher.run_mesher(
        inputs,
        output_filename=parsed_args.output_filename,
        verbose=not parsed_args.quiet,
        overwrite_file=parsed_args.overwrite_file,
        generate_plots=parsed_args.generate_plots)


if __name__ == "__main__":  # pragma: no cover
    main()