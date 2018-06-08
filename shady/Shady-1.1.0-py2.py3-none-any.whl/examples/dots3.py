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
import numpy
import Shady

if __name__ == '__main__':
	cmdline = Shady.WorldConstructorCommandLine( canvas=True )
	ndots  = cmdline.Option( 'ndots', 300,   type=int, container=None )
	nsides = cmdline.Option( 'sides',   5,   type=int, min=3, container=None )
	radius = cmdline.Option( 'radius', 25.0, type=( int, float ), container=None )
	spin   = cmdline.Option( 'spin',    0.2, type=( int, float ), container=None )
	shell  = cmdline.Option( 'shell', False, type=bool, container=None )
	cmdline.Finalize()

	if ( nsides + 1 ) * ndots > Shady.Rendering.MAX_POINTS: raise ValueError( '(sides + 1) * ndots cannot exceed %d' % Shady.Rendering.MAX_POINTS )
	
	w = Shady.World( **cmdline.opts )
	
	field = w.Stimulus( Shady.PackagePath( 'examples/media/waves.jpg' ), size=w.size, visible=0 )
	field.carrierTranslation = ( field.envelopeSize - field.textureSize ) // 2 
	field.carrierScaling = max( field.envelopeSize.astype( float ) / field.textureSize )
	shape = Shady.ComplexPolygonBase( nsides )
	locations = numpy.random.uniform( low=[ 0, 0 ], high=field.size, size=[ ndots, 2 ] )
	velocity = numpy.random.uniform( low=[ -30, -30 ], high=[ +30, -150 ], size=[ ndots, 2 ] )
	func = Shady.Integral( lambda t: velocity ) # we could say just Shady.Integral( velocity ) but then we wouldn't be able to change the velocity on-the-fly
	func += locations
	func %= field.size # wrap around the field, pacman-style
	func.Transform( Shady.Real2DToComplex )      # ndots-by-1 complex
	func += lambda t: radius * shape * 1j ** ( 4.0 * spin * t )  # 1-by-(sides+1) complex
	# numpy broadcasting in the `+` operator does the rest
	field.Set( points=func, drawMode=Shady.DRAWMODE.POLYGON, visible=1 )

	Shady.AutoFinish( w, shell=shell )
