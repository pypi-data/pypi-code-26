# -*- coding: utf-8 -*-
# Copyright (c) 2017, System Engineering Software Society
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the System Engineering Software Society nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL SYSTEM ENGINEERING SOFTWARE SOCIETY BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import json

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


class CreateJSON(synode.Node):
    """
    Manually Create JSON by writing a python expression which evaluates
    to a dictionary containing normal python values, that is, dictionaries
    lists, floats, integers, strings and booleans.

    Optional input port, named arg, can be used in the expression. Have a look
    at the :ref:`Data type APIs<datatypeapis>` to see what methods and
    attributes are available on the data type that you are working with.
    """

    name = 'Manually Create JSON'
    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    copyright = '(C) 2017 System Engineering Software Society'
    version = '0.1'
    icon = 'create_json.svg'
    tags = Tags(Tag.Input.Generate)

    nodeid = 'org.sysess.sympathy.create.createjson'
    inputs = Ports([Port.Custom('<a>', 'Input',
                                name='arg', n=(0, 1))])
    outputs = Ports([Port.Json('Output', name='output')])

    parameters = synode.parameters()
    parameters.set_string(
        'code',
        description='Python expression that evaluates to a dictionary.',
        value='{}  # Empty dictionary.',
        editor=synode.Util.code_editor().value())

    def execute(self, node_context):
        inputs = node_context.input.group('arg')
        arg = inputs[0] if inputs else None
        env = {'arg': arg}
        dict_ = eval(compile(node_context.parameters['code'].value,
                             '<string>', 'eval'),
                     env, env)
        node_context.output[0].set(dict_)


class JSONtoText(synode.Node):
    """
    JSON to Text.
    """

    name = 'JSON to Text'
    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    copyright = '(C) 2017 System Engineering Software Society'
    version = '1.0'
    icon = 'create_json.svg'
    tags = Tags(Tag.DataProcessing.Convert)

    nodeid = 'org.sysess.sympathy.convert.jsontotext'
    inputs = Ports([Port.Json('Input', name='input')])
    outputs = Ports([Port.Text('Output', name='output')])

    parameters = synode.parameters()

    def execute(self, node_context):
        node_context.output[0].set(
            json.dumps(node_context.input[0].get()))


class TexttoJSON(synode.Node):
    """
    Text to JSON.
    """

    name = 'Text to JSON'
    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    copyright = '(C) 2017 System Engineering Software Society'
    version = '1.0'
    icon = 'create_json.svg'
    tags = Tags(Tag.DataProcessing.Convert)

    nodeid = 'org.sysess.sympathy.convert.texttojson'
    inputs = Ports([Port.Text('Input', name='input')])
    outputs = Ports([Port.Json('Output', name='output')])

    parameters = synode.parameters()

    def execute(self, node_context):
        node_context.output[0].set(
            json.loads(node_context.input[0].get()))
