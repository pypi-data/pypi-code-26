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
import Shady
import Shady.Text

cmdline = Shady.WorldConstructorCommandLine()
cmdline.Finalize()

world = Shady.World( gamma=-1, **cmdline.opts )

grating = world.Sine( size=500, sigf=.0125, position=world.Place( -0.9, 0 ), anchor=[ -1, 0 ], pp=0, bg=127./255 )

enhanced = Shady.Loupe( grating, position=grating.Place( +1.2, 0 ), anchor=[ -1, 0 ], scaling=4, update_period=1.0 )

bitStealing = world.LookupTable( Shady.PackagePath( 'examples/BitStealingLUT_maxDACDeparture=2_Cmax=3.0_nbits=16_gamma=sRGB.npz' ) )

grating.rounding = True
approxBG = [ 0.5, 0.5, 0.5 ]
@world.AnimationCallback
def WrangleBackground( t=None ):
	gamma = [ 1.0, 1.0, 1.0 ] if grating.lut else grating.gamma
	maxDAC = world.ditheringDenominator
	targetDAC[ : ] = [ int( maxDAC * Shady.Linearize( val, gamma=g ) ) + ( 0 if grating.rounding else 0.5 ) for val, g in zip( approxBG, gamma ) ]
	grating.bg = [ Shady.ScreenNonlinearity( val / maxDAC, gamma=g ) for val, g in zip( targetDAC, gamma ) ]
targetDAC = [];
WrangleBackground()

msg = world.Stimulus( position=grating.Place( 0, -1.2 ), anchor=[ 0, +1 ]  )
def caption( t ):
	txt = '%g%% contrast\n' % ( grating.contrast * 100 )
	if grating.lut: txt += '%d-element look-up table' % grating.lut.length
	else: txt += ( 'dithering off\n' if grating.ditheringDenominator <= 0.0 else 'dithering on\n' ) + 'gamma = ' + str( list( grating.gamma ) )
	if grating.lut or grating.rednoise: txt += '\nnoise = %g' % grating.rednoise
	txt += '\nraw BG = %r' % targetDAC
	return txt
msg.text = caption

f = Shady.FrameIntervalGauge( world )
instructions = world.Stimulus( position=world.Place( -1 ), anchor=-1, text="""\
  up / down  :  raise/lower contrast
left / right :  slower/faster capture rate
     d       :  toggle dithering
     g       :  toggle gamma-correction
     n       :  toggle additive noise
     l       :  toggle look-up table
     b       :  toggle integer/non-integer background DAC
   + / -     :  increase/decrease magnification
""", text_size=20 )


@world.EventHandler( slot=-1 )
def HandleEvent( self, event ):
	if event.type in [ 'key_release' ]:
		if event.key in [ 'right' ] and enhanced.update_period > 0.005: enhanced.update_period /= 2.0
		if event.key in [ 'left' ]  and enhanced.update_period < 30:    enhanced.update_period *= 2.0
		if event.key in [ 'down' ]:  grating.contrast /= 2.0
		if event.key in [ 'up' ]:    grating.contrast *= 2.0
		if event.key in [ 'd' ]:     grating.ditheringDenominator *= -1
		if event.key in [ 'l' ]:     grating.lut = None if grating.lut else bitStealing
		if event.key in [ 'n' ]:     grating.noise = 0 if any( grating.noise ) else 1e-4
		if event.key in [ 'g' ]:     grating.gamma = world.gamma if ( grating.gamma[ 0 ] == 1.0 ) else 1.0
		if event.key in [ 'b' ]:     grating.rounding = not grating.rounding; WrangleBackground()
		enhanced.update_now = True
	if event.type in [ 'text' ]:
		if event.text in [ '-' ]:       enhanced.scaling /= 2.0
		if event.text in [ '+', '=' ]:  enhanced.scaling *= 2.0
		enhanced.update_now = True
Shady.AutoFinish( world )
