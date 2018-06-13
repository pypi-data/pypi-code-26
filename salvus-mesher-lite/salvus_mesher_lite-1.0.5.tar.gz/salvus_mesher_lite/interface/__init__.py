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
import collections
import json
import os

from jsonschema import Draft4Validator

from ..compat import PY2


# Do a bit of preprocessing by opening the schema, making sure its actually
# valid, and converting it to something a bit more digestible later on.

# Open the schema.
with open(os.path.join(os.path.dirname(__file__), "schemas",
                       "salvus_mesher_lite_0.0.1.json"),
          mode="rb" if PY2 else "rt") as fh:
    # Preserve order.
    _SCHEMA = json.load(fh, object_pairs_hook=collections.OrderedDict)


def __resolve_ref(ref):
    path = [_i for _i in ref.split("/") if _i != "#"]
    p = _SCHEMA
    for _p in path:
        p = p[_p]
    return p


def __resolve_schema(schema):
    def _walk_dict(s):
        for key, value in s.items():
            if isinstance(value, dict):
                if list(value.keys()) == ["$ref"]:
                    s[key] = __resolve_ref(value["$ref"])
                else:
                    _walk_dict(value)
    _walk_dict(schema["definitions"])


__resolve_schema(_SCHEMA)

# Validate it.
Draft4Validator.check_schema(_SCHEMA)

# Parse the scheme to something that is slightly more digestible.
# Groups are lower level constructs like "spherical", "mesh3D", and so on
# that are later combined to form mesh types.
_GROUPS = {}
for key, value in _SCHEMA["definitions"]["properties"].items():
    # groups need to contain at least a description, title and properties
    if all(v in value for v in ['description', 'title', 'properties']):
        _GROUPS[key] = {
            "description": value["description"],
            "title": value["title"],
            "arguments": value["properties"]
        }


# The mesh types are the higher level constructs like Globe3D and
# SphericalChunk3D.
_MESH_TYPES = collections.OrderedDict()
for mt in _SCHEMA["allOf"][0]["properties"]["mesh_type"]["enum"]:
    props = [
        _i["allOf"][0]
        for _i in _SCHEMA["allOf"][1]["anyOf"]
        if _i["allOf"][0]["properties"]["mesh_type"]["enum"] == [mt]][0]

    _MESH_TYPES[mt] = {
        "description": props["properties"]["mesh_type"]["description"],
        "required_groups": props["required"],
        # The first group is always the mesh type so it can be skipped.
        "all_groups": list(props['properties'].keys())[1:]
    }


# The command used to call it.
_CMD = "python -m salvus_mesher_lite.interface"