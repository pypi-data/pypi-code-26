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

import itertools
from jsonschema import ValidationError
from jsonschema import validate as json_validate
import json
import re
import sys

from . import _SCHEMA


def validate_inputs(inputs, exit_with_pretty_error_msg=False):
    """
    Validates the input against the JSON schema.

    :tyoe inputs: dict
    :param inputs: The input parameters as a dictionary.
    :tyoe exit_with_pretty_error_msg: bool
    :param exit_with_pretty_error_msg: Try to exit with a prettier and more
        useful error message in case an error happens.
    """
    # Get rid of all non-JSONable things.
    inputs = json.loads(json.dumps(inputs))
    # Do the same with the schema to not have the ordered dict anymore which
    # destroys the error messages.
    schema = json.loads(json.dumps(_SCHEMA))

    def _rm_unicode_prefix(_s):
        return re.sub(r"u'", "'", _s)

    try:
        json_validate(inputs, schema)
    except ValidationError as e:  # pragma: no cover
        if exit_with_pretty_error_msg is False:
            raise

        print("Inputs failed validation against the schema.\n" +
              "================================================\n")
        print(e)
        # Try to produce actually helpful error messages.
        print("\n================================================")
        print("\nAttempting to produce more helpful error messages:\n")
        if e.context:
            msgs = []
            for _e in e.context:
                if "required property" in _e.message.lower() or \
                        "additional properties" in _e.message.lower():
                    continue
                p = ["[%i]" % _i if isinstance(_i, int) else _i
                     for _i in _e.absolute_path]
                msgs.append(" - '%s': %s" % (".".join(p),
                                             _rm_unicode_prefix(_e.message)))
                msgs[-1] = msgs[-1].replace(".[", "[")
            _duplicate_msgs = [
                key for key, group in itertools.groupby(sorted(msgs))
                if len(list(group)) > 1]
            _printed_msgs = []
            for msg in msgs:
                if msg not in _duplicate_msgs:
                    continue
                if msg in _printed_msgs:
                    continue
                print(msg)
                _printed_msgs.append(msg)
        # Fallback - not sure if it can even be triggered.
        else:  # pragma: no cover
            print(" - '%s': %s" % (".".join(e.absolute_path),
                                   _rm_unicode_prefix(e.message)))
        print("\n")
        sys.exit(1)