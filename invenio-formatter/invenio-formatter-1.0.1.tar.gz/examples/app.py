# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Minimal Flask application example.

SPHINX-START

First install Invenio-Formatter by running:

.. code-block:: console

    $ pip install -e .[all]
    $ cd examples

Next, start the development server:

.. code-block:: console

   $ export FLASK_APP=app.py FLASK_DEBUG=1
   $ flask run

and open the example application in your browser:

.. code-block:: console

    $ open http://127.0.0.1:5000/

SPHINX-END

"""

from __future__ import absolute_import, print_function

import datetime
from os.path import dirname, join

import jinja2
from flask import Flask, render_template

from invenio_formatter import InvenioFormatter

# Create Flask application
app = Flask(__name__)

InvenioFormatter(app)

# Set jinja loader to first grab templates from the app's folder.
app.jinja_loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader(join(dirname(__file__), "templates")),
    app.jinja_loader
])


@app.route('/', methods=['GET'])
def index():
    """Example format date."""
    mydate = datetime.date.today()
    return render_template('index.html', mydate=mydate)
