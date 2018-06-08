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
import Shady
import Shady.Video

cmdline = Shady.WorldConstructorCommandLine( width=1000, height=750 )
shell     = cmdline.Option( 'shell',     False, type=bool, container=None )
source    = cmdline.Option( 'source',    Shady.PackagePath( 'examples/media/fish.mp4' ),  type=( int, str ), container=None )
loop      = cmdline.Option( 'loop',      True,  type=bool, container=None )
transform = cmdline.Option( 'transform', False, type=bool, container=None )
multi     = cmdline.Option( 'multi',     0,     type=int,  container=None )
cmdline.Help().Finalize()

w = Shady.World( **cmdline.opts )
s = w.Stimulus( video=source, bgalpha=0 )
s.video.Play( loop=loop )


if transform:
	def Desaturated( x ):
		grey = x[ :, :, :3 ].mean( axis=2 )
		x[ :, :, 0 ] = grey
		x[ :, :, 1 ] = grey
		x[ :, :, 2 ] = grey
		return x
	sm = Shady.StateMachine()
	@sm.AddState
	class DoNothing( Shady.StateMachine.State ):
		duration = 3
		def onset( self ):
			s.video.Transform = None
		next = 'TransformNewData'
	@sm.AddState
	class TransformNewData( Shady.StateMachine.State ):
		duration = 3
		def onset( self ):
			s.video.Transform = lambda x, changed: Desaturated( x ) if changed else None
		next = 'ReturnOriginalEveryTime'
	@sm.AddState
	class ReturnOriginalEveryTime( Shady.StateMachine.State ):
		duration = 3
		next = 'TransformEveryTime'
		def onset( self ):
			s.video.Transform = lambda x, changed: x
	@sm.AddState
	class TransformEveryTime( Shady.StateMachine.State ):
		duration = 3
		def onset( self ):
			s.video.Transform = lambda x, changed: Desaturated( x )
		next = 'DoNothing'
	s.SetAnimationCallback( sm )

if multi:
	def Spawn():
		s.plateauProportion = 1 # oval
		s.video.aperture = min( s.video.aperture ) # circular
		for i in range( multi ):
			cyclical_offset = i / float( multi )
			cycle = Shady.Integral( 0.2 ) + cyclical_offset
			child = w.Stimulus( s ).Inherit( s ).Set(
				position = Shady.Apply( s.Place, cycle * 360, polar=True ),
				anchor = Shady.Apply( Shady.Sinusoid, cycle, phase_deg=[ 270, 180 ] ),
				#anchor = -1, angle = cycle * 360,
				scaling = 0.2,
			)
	w.Defer( Spawn ) # TODO: necessary?
Shady.AutoFinish( w, shell=shell )

