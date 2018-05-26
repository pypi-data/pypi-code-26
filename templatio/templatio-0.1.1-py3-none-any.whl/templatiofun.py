#==============================================================================
# Copyright 2018 Marco Bellaccini - marco.bellaccini[at!]gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#==============================================================================

#==============================================================================
# templatio
#
# templatio is a Python 3 utility that uses TextFSM and Jinja2 to convert
# text files based on input and output templates.
# It supports TextFSM syntax for input templates and Jinja syntax for output
# templates.
#
# TextFSM Wiki: https://github.com/google/textfsm/wiki/TextFSM
# Jinja2 website: http://jinja.pocoo.org/
#
#==============================================================================

import textfsm
from jinja2 import Template, exceptions
from io import StringIO

# parse input data with input template
# and get output data using output template
def parseInToOut(intempl, outtempl, inData):
    # build regexp table from input template data
    # in case of invalid input template, raise a readable exception
    # containing TestFSM exception message
    try:
        re_table = textfsm.TextFSM(StringIO(intempl))
    except textfsm.TextFSMTemplateError as tmpex:
        raise ValueError("Error: invalid input template.\n" + str(tmpex))
    
    # build output template from output template data
    # in case of invalid output template, raise a readable exception
    # containing Jinja2 exception message
    try:
        outtemplate = Template(outtempl)
    except exceptions.TemplateSyntaxError as tmpex:
        raise ValueError("Error: invalid output template.\n" + str(tmpex))
    
    # parse data from input file using input template
    parsedData = re_table.ParseText(inData)
    
    # build a dictionary with parsed data
    # if no match w.r.t. input template, use empty dictionary
    if 0 != len(parsedData):
        # for each Value, get first match only 
        # (no multi-match support - for now)
        pdict = dict(zip(re_table.header, parsedData[0]))
    else:
        pdict = dict()
    
    # render parsed data using output template
    try:
        renderedData = outtemplate.render(**pdict)
    # when type mismatch occurs during rendering
    # (e.g. due to a comparison between an integer and a string)
    # this will catch it
    except TypeError as tmpex:
        raise ValueError(("Error: unable to render content "
                          "using output template.\n") + str(tmpex))
    
    return renderedData
