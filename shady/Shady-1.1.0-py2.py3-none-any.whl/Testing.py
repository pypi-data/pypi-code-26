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
__all__ = [
	'Test',
]

# Python standard library modules
import os
import sys
import socket



def Test():

	import Shady, Shady.Text
	
	cmdline = Shady.CommandLine()
	script = cmdline.Option( 'script', '', type=str, position=0 )
	cmdline = Shady.WorldConstructorCommandLine( cmdline.Delegate(), debugTiming=True, logfile='{}.log' )
	opts = dict( cmdline.Finalize().opts )
	
	Shady.BackEnd( windowing=opts[ 'backend' ], acceleration=opts[ 'acceleration' ] )
	screens = Shady.Screens()
	
	class TestWorld( Shady.World ):
		def HandleEvent( self, event ):
			if event.type == 'key_release' and event.key in [ 'q', 'escape' ]:
				if self.logger and 'caption' in self.stimuli:
					self.stimuli.caption.Set( z=-1.0, text = 'saving diagnostic info...' )
				self.Defer( self.Defer, self.Defer, self.Close ) # !!  :-s
		def TestSetup( self ):
			pass
		def Prepare( self, screenInfo, numberOfScreens ):
			computerName = os.path.splitext( socket.gethostname() )[ 0 ].lower()
			self.logger.logSystemInfoOnClose = True
			self.logger.Log( computerName=computerName, screenInfo=screenInfo, worldSize=self.size )
			txt = self.TestSetup()
			if txt is not None:
				logName = self.logger.filename 
				txt = "Computer = %r\nScreen %d of %d: %g x %g -> %g x %g\nLogfile = %s%s" % (
					computerName,
					screenInfo[ 'number' ],
					numberOfScreens,
					screenInfo[ 'width' ],
					screenInfo[ 'height' ],
					self.width,
					self.height,
					( logName if logName else repr( logName ) ),
					( ( '\n\n' + txt ) if isinstance( txt, str ) and txt else '' ),
				)
				caption = self.Stimulus(
					name = 'caption',
					text = txt,
					color = [ 1, 0.5, 0 ],
					z = -1.0,
					position = self.Place( -1, -1 ),
					anchor = [ -1, -1 ],
				)
				caption.text.Set( bg=( 0, 0, 0 ), border=( 2, 2 ) )
	def WrapExec( code, ns ):
		exec( code, ns, ns )
	
	if script:
		if not os.path.isfile( script ) and hasattr( Shady, script ):
			TestWorld.TestSetup = getattr( Shady, script )
		else:
			for qualified in [ script, script + '.py', Shady.PackagePath( 'tests', script + '.py' ), Shady.PackagePath( 'tests', script ) ]:
				if os.path.isfile( qualified ): script = qualified; break
			else: raise IOError( 'failed to find file %r' % script )
			with open( script, 'rt' ) as fh: code = fh.read()
			user_ns = {}
			compiled = compile( code, script, 'exec' )
			WrapExec( code, user_ns )
			method = user_ns.get( 'TestSetup', None )
			if not callable( method ): raise ImportError( 'no `TestSetup()` method definition found in %s' % script )
			TestWorld.TestSetup = user_ns[ 'TestSetup' ]
		

	for screen in screens:
		opts[ 'screen' ] = screen[ 'number' ]
		world = TestWorld( screenInfo=screen, numberOfScreens=len( screens ), **opts )	
		world.Run()
