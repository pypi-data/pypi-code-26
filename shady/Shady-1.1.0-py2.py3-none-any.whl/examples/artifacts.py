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
"""
DOC-TODO
"""
import os
import sys
import numpy
import Shady

w = Shady.World( gamma=-1, bg=0.5 )
size = min( w.width // 3 - 100, w.height // 2 - 100 )
xshift = size * 1.1
yshift = ( w.height + size ) // 6
noise = numpy.random.uniform( size=[ size, size ] )
s1 = w.Stimulus( noise, x=-xshift, y=-yshift, atmosphere=w )
s2 = w.Stimulus( noise, x=0,       y=-yshift, atmosphere=w )
s3 = w.Stimulus( noise, x=+xshift, y=-yshift, atmosphere=w )
s4 = w.Stimulus( noise, x=-xshift, y=+yshift )
s5 = w.Stimulus( noise, x=0,       y=+yshift, atmosphere=s4 )
s6 = w.Stimulus( noise, x=+xshift, y=+yshift, atmosphere=s4  )

freq = 0.5
s4.envelopeRotation = s1.envelopeRotation = Shady.Oscillator( freq ) * 2
s5.envelopeScaling  = s2.envelopeScaling  = Shady.Oscillator( freq ) * 0.02 + 1.0
s6.envelopeOrigin   = s3.envelopeOrigin   = Shady.Oscillator( freq ) * 1.0
#Shady.Utilities.AdjustGamma( w )

@w.EventHandler( slot=1 )
def eh( self, event ):
	if event.type == 'text' and event.text == '0': 
		s4.ResetClock()
		s5.ResetClock()
		s6.ResetClock()
