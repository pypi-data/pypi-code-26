#!/usr/bin/env python
# $BEGIN_SHADY_LICENSE$
# 
# This file is part of the Shady project, a Python framework for
# real-time manipulation of psychophysical stimuli for vision science.
# 
# Copyright (C) 2017-18  Jeremy Hill, Scott Mooney
# 
# Shady is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_SHADY_LICENSE$

import sys
import Shady

if not hasattr( sys, 'argv' ): sys.argv = []

subcommands = dict(
	demo = Shady.Utilities.RunShadyScript,
	run = lambda: Shady.Utilities.RunShadyScript( sys.argv, console=None ), # TODO: better than before, but still somewhat hacky
	test = Shady.Testing.Test,
	timings = lambda: Shady.PlotTimings( sys.argv ),
)

main = subcommands.get( sys.argv[ 1 ].lower(), 'unrecognized' ) if len( sys.argv ) >= 2 else 'absent'
if main in [ 'unrecognized', 'absent' ]: main = subcommands[ 'run' ]
else: sys.argv.pop( 1 )
main()
