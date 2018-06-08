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
The Dynamics module contains a number of objects that are
designed to perform discretized real-time processing of
arbitrary functions.

DOC-TODO

Note that all everything exported from this module is also available
in the top-level `Shady.` namespace.
"""

__all__ = [
	'Clock',
	'Function',
	'Integral', 'Derivative', 'ResetTimeBase',
	'Impulse', 'Smoother',
	'Sinusoid', 'Oscillator',
	'Transition', 'RaisedCosine',
	'Apply',
	'StateMachine',
]

import copy
import math
import inspect
import weakref
import operator
import functools
import collections

numpy = None
try: import numpy
except: pass

IDCODE = property( lambda self: '0x%08x' % id( self ) )

class Stop( StopIteration ):
	"""
	This a type of `Exception` - specifically, a subclass of `StopIteration`.
	It is raised internally when a `Function`'s "watcher" callback (set using
	`Function.Watch()`) returns a numeric argument, or a numeric sequence
	or array).  The `Function` will continue to transform this terminal value
	according to its existing chain, but at the very last stage of the chain
	it will throw another `Stop()` containing the transformed terminal value.
	
	Some frameworks (e.g. `Shady.PropertyManagement`) will automatically catch
	and deal with this type of exception.
	"""
	def __init__( self, arg ): StopIteration.__init__( self, arg )
	
class Abort( StopIteration ):
	"""
	This a type of `Exception` - specifically, a subclass of `StopIteration`.
	It is raised when a `Function`'s "watcher" callback (set using
	`Function.Watch()`) returns a `dict` argument. Unlike a `Stop` exception,
	the `Function` chain will not catch, transform and re-throw this type
	of exception.
	
	Some frameworks (e.g. `Shady.PropertyManagement`) will automatically catch
	and deal with this type of exception.
	"""
	def __init__( self, arg ): StopIteration.__init__( self, arg )
	
class Function( object ):
	"""
	DOC-TODO
	"""
	__slots__ = [ 'terms' ]
	id = IDCODE
	
	def __init__( self, *pargs, **kwargs ):
		if not hasattr( self, 'terms' ): self._init( *pargs, **kwargs )	
	def _init( self, *pargs, **kwargs ):
		self.terms = []
		while pargs:
			other = pargs[ 0 ]
			if type( self ) is not type( other ): break
			pargs = pargs[ 1: ]
			self.terms[ : ] = copy.deepcopy( other.terms )
			if self.terms: break
		for arg in pargs:
			if kwargs and callable( arg ): arg = functools.partial( arg, **kwargs )
			self += arg
		return self

	def __call__( self, *pargs, **kwargs ):
		#print('%r is being called with %r and %r' % ( self, pargs, kwargs ))
		result = None
		stopped = False
		for mode, opfunc, term in self.terms:
			if mode == 'through':
				pp, kk = opfunc
				opfunc = None
				term = term( result, *pp, **kk )
			elif mode == 'watch':
				if result is None: continue
				pp, kk = opfunc
				opfunc = None
				stopValue = term( result, *pp, **kk )
				if stopValue is None: continue
				if isinstance( stopValue, dict ): raise Abort( stopValue )
				term = stopValue
				stopped = True
			elif callable( term ):
				try: term = term( *pargs, **kwargs )
				except Stop as exc:
					term = exc.args[ 0 ]
					stopped = True
			if isinstance( term, Exception ): raise term
			if numpy is not None and term is not None and not isinstance( term, ( int, float, complex, str, numpy.ndarray ) ):
				try: term = numpy.array( term, dtype=float, copy=False )
				except: term = numpy.array( term, dtype=complex, copy=False )
			if result is None or opfunc is None: result = term
			elif mode == 'LR':  result = opfunc( result, term )
			elif mode == 'RL':  result = opfunc( term, result )
			else: raise ValueError( 'internal error - unexpected mode' )
		if stopped: raise Stop( result )
		return result
	
	def __repr__( self ): return '<%s %s>' % ( self.__class__.__name__, self.id )
	def __str__( self ):
		s = repr( self )
		for iTerm, ( mode, opfunc, term ) in enumerate( self.terms ):
			isLast = ( iTerm == len( self.terms ) - 1 )
			if mode == 'through':
				pp, kk = opfunc
				s += TreeBranch( 'through %s( <>%s%s )' % ( term.__name__, ''.join( ', %r' % arg for arg in pp ), ''.join( ', %s=%r' % item for item in kk.items() ) ) )
			else:
				if iTerm: s += TreeBranch( '%s %r' % ( mode, opfunc ) )
				s += TreeBranch( term, last=isLast )
		return s
		
	def __neg__( self ): return 0 - self
	def __pos__( self ): return self
	def __abs__( self ): return self.Transform( abs )
	
	def Transform( self, any_callable, *additional_pargs, **kwargs ):
		"""
		DOC-TODO
		"""
		if isinstance( any_callable, str ): self.terms.append( ( 'RL', operator.mod, any_callable ) )
		else: self.terms.append( ( 'through', ( additional_pargs, kwargs ), any_callable ) )
		return self
	Through = Transform
	
	
	def Watch( self, conditional, *additional_pargs, **kwargs ):
		"""
		Adds a watch condition on the output of a `Function`.
		
		Args:
		
		    conditional (callable):
		        This should be a callable whose first input
		        argument is a `float`, `int` or numeric `numpy`
		        array.  The return value can be:
		        
		        * `None`, in which case nothing happens
		        
		        * a `dict` `d`, in which case the `Function`
		          will raise an `Abort` exception (a subclass
		          of `StopIteration`) containing `d` as the
		          exception's argument.  The `Function` itself
		          will not perform any further processing.
		          
		        * a numeric value (or numeric array) `x`, in
		          which case the `Function` will continue to
		          process the numeric value but, at the very
		          last step in the chain, it will raise a
		          `Stop` exception (a subclass of
		          `StopIteration`) containing the final
		          processed value.
		
		    *additional_pargs:
		        If additional positional arguments are supplied,
		        they are simply passed through to `conditional`.
		        
		    **kwargs:
		        If additional keyword arguments are supplied,
		        they are simply passed through to `conditional`.
		
		Some frameworks (e.g. `Shady.PropertyManagement`) will
		automatically catch and deal with `StopIteration` exceptions
		appropriately, but if you need to do so manually, you can do
		so as follows::
		
		    try:
		        y = f( t )
		    except StopIteration as exc:
		        info = exc.args[ 0 ]
		        if not isinstance( info, dict ):
		            terminal_value_of_y = info
		"""
		#TODO: need a demo of this in conjunction with PropertyManagement/Shady dynamics:
		#      functionInstance.Watch(
		#          lambda f:  None if f < 10 else {'visible':0}
		#      )
		self.terms.append( ( 'watch', ( additional_pargs, kwargs ), conditional ) )
		return self
	
	def Tap( self, initial=None ): return Tap( self, initial=initial )

class Tap( object ):
	def __init__( self, f, initial=0.0 ): self.container = [ initial ]; f.Watch( self._watch )
	def _watch( self, result ): self.container[ : ] = [ result ]
	def __call__( self ): return self.container[ 0 ]
		
def TreeBranch( txt, spacers=1, last=False ):
	blank   = '       '
	bar     = ' |     '
	branch  = ' +---- '
	indent  = blank if last else bar
	lines = str( txt ).replace( '\r\n', '\n' ).replace( '\r', '\n' ).split( '\n' )
	s = ( '\n' + bar ) * spacers + '\n'
	return s + '\n'.join( ( indent if iLine else branch ) + line for iLine, line in enumerate( lines ) )

def MakeOperatorMethod( optype, opname ):
	if opname == 'div': opname = 'truediv'
	opfunc = getattr( operator, opname + '_', None )
	if opfunc is None: opfunc = getattr( operator, opname )
	def func( instance, other ):
		if optype == 'i':
			mode = 'LR'
		else:
			if   optype == 'l': mode = 'LR'
			elif optype == 'r': mode = 'RL'
			else: raise ValueError( 'internal error - unexpected mode' )
			instance = copy.deepcopy( instance )
		instance.terms.append( ( mode, opfunc, copy.deepcopy( other ) ) )
		return instance
	return func
	
for opname in 'add sub mul truediv div floordiv pow mod and or xor'.split():
	setattr( Function, '__'  + opname + '__', MakeOperatorMethod( 'l', opname ) )
	setattr( Function, '__r' + opname + '__', MakeOperatorMethod( 'r', opname ) )
	setattr( Function, '__i' + opname + '__', MakeOperatorMethod( 'i', opname ) )

def Apply( any_callable, f, *additional_pargs, **kwargs ):
	"""
	::
		g = Apply( some_function, f )     # g and f are both `Function` instances
		
	is equivalent to::
	
		copy.deepcopy( f ).Transform( some_function )
	
	In both cases, `some_function()` is applied to the output of f.
	"""
	return copy.deepcopy( f ).Transform( any_callable, *additional_pargs, **kwargs )

def Impulse( magnitude=1.0 ):
	"""
	A very simple specially-configured `Function` instance, which will
	return `magnitude` the first time it is called (or when called again
	with the same `t` argument as its first call) and then return `0.0`
	if called with any other value of `t`.
	"""
	_t0 = [ None ]
	def impulse_core( t, *pargs, **kwargs ):
		t0 = _t0[ 0 ]
		if t0 is None: t0 = _t0[ 0 ] = t
		return magnitude if t == t0 else 0.0
	return Function( impulse_core )

def Sinusoid( cycles, phase_deg=0 ):
	"""
	Who enjoys typing `2.0 * numpy.pi *` over and over again?
	This is a wrapper around `numpy.sin` (or `math.sin` if `numpy`
	is not installed) which returns a sine function of an argument
	expressed in cycles (0 to 1 around the circle).  Heterogeneously,
	but hopefully intuitively, the optional phase-offset argument
	is expressed in degrees. If `numpy` is installed, either
	argument may be non-scalar (`phase_deg=[90,0]` is useful for
	converting an angle into 2-D Cartesian coordinates).
	
	This is a function,  but not a `Function`.  You may be
	interested in `Oscillator`, which returns a `Function`.
	"""
	if numpy: return numpy.sin( 2.0 * numpy.pi * ( numpy.asarray( cycles, float ) + numpy.asarray( phase_deg, float ) / 360.0 ) )
	else:     return math.sin(  2.0 * math.pi  * ( float( cycles )                + float( phase_deg )                / 360.0 ) )
		
def Oscillator( freq, phase_deg=0.0 ):
	"""
	Returns a `Function` object with an output that oscillates
	sinusoidally as a function of time: the result of `Apply`ing
	`Sinusoid` to an `Integral`.
	"""
	return Apply( Sinusoid, Integral( freq ), phase_deg=phase_deg )

def Clock( startNow=True, speed=1.0 ):
	"""
	DOC-TODO
	"""
	if numpy: speed = numpy.asarray( speed, dtype=float )
	if startNow:
		t0 = []
		def clock( t ):
			if not t0: t0.append( t )
			return speed * ( t - t0[ 0 ] )
	else:
		clock = lambda t: speed * t
	return Function( clock )

def Smoother( arg=None, sigma=1.0, exponent=2.0 ):
	"""
	DOC-TODO
	"""
	return Function( _SmoothingWrapper( arg, sigma=sigma, exponent=exponent ) )
	
class _SmoothingWrapper( object ):
	__slots__ = [ 'func', 'sigma', 'exponent', 'memory', 'lastOutput' ]
	id = IDCODE
	def __init__( self, func, sigma, exponent ):
		self.memory = {}
		self.func = func
		self.sigma = float( sigma )
		if isinstance( exponent, str ) and exponent.lower() == 'ewa': exponent = None 
		self.exponent = exponent
		self.lastOutput =  None
	def __repr__( self ): return '<%s %s>' % ( self.__class__.__name__, self.id )
	def __str__( self ): return repr( self ) + TreeBranch( self.func, last=True )
	def __call__( self, t, *pargs, **kwargs ):
		if t is None: return self.lastOutput
		x, y = self.memory.get( t, ( None, None ) )
		if y is not None: self.lastOutput = y; return y
		if x is None:
			x = self.func
			if callable( x ): x = x( t, *pargs, **kwargs )
		if numpy: x = numpy.array( x, dtype=float, copy=True )
		if x is None or not self.sigma: self.lastOutput = x; return x
		self.memory[ t ] = ( x, None )
		if self.exponent is None: y = self.EWA( t )
		else: y = self.FIR( t )
		self.memory[ t ] = ( x, y )
		self.lastOutput = y
		return y
		
	def FIR( self, t ): # Gaussian-weighted with sigma interpreted as standard deviation
		sumwx = sumw  = 0.0
		for ti, ( xi, yi ) in list( self.memory.items() ):
			nsig = abs( t - ti ) / self.sigma
			if nsig > 5.0: del self.memory[ ti ]; continue
			if self.sigma == 0.0: wi = 1.0
			else: wi = math.exp( -0.5 * nsig ** self.exponent )
			sumw  = sumw  + wi
			sumwx = sumwx + wi * xi
		return sumwx / sumw			
	def EWA( self, t ): # exponential weighted average (IIR of order 1) with sigma interpreted as half-life
		items = sorted( self.memory.items() )
		tcurr, ( xcurr, ycurr ) = items[ -1 ]
		if len( items ) == 1: return xcurr
		tprev, ( xprev, yprev ) = items[ -2 ]
		self.memory = dict( items[ -2: ] )
		lambda_ = 0.5 ** ( ( tcurr - tprev ) / self.sigma )
		return lambda_ * yprev + ( 1.0 - lambda_ ) * xcurr
			
			
def Integral( *pargs, **kwargs ):
	r"""
	Returns a specially-configured `Function`. Like the `Function` constructor,
	the terms wrapped by this call may be numeric constants, and/or callables that
	take a single numeric argument `t`.   And like any `Function` instance, the
	instance returned by `Integral` is itself a callable object that can be
	called with `t`.
	
	Unlike a vanilla `Function`, however, an `Integral` has memory for values
	of `t` on which it has previously been called, and returns the *cumulative*
	area under the sum of its wrapped terms, estimated discretely via the
	trapezium rule at the distinct values of `t` for which the object is called.
	
	Like any `Function`, it can interact with other `Functions`, with other
	single-argument callables, with numeric constants, and with numeric
	`numpy` objects via the standard arithmetic operators `+`, `-`, `/`,
	`*`, `**`, and `%`, and may also have other functions applied to its
	output via `Apply`.
	
	`Integral` may naturally be take another `Integral` output as its input,
	or indeed any other type of `Function`.
	
	Example - prints samples from the quadratic :math:`\frac{1}{2}t^2 + 100`:: 
	    
	    g = Integral( lambda t: t ) + 100.0
	    print( g(0) )
	    print( g(0.5) )
	    print( g(1.0) )
	    print( g(1.5) )
	    print( g(2.0) )
	
	"""
	if not pargs: pargs = ( 1.0, ) 
	integrate = kwargs.pop( 'integrate', 'trapezium' )
	if integrate not in [ 'trapezium', 'rectangle' ]: raise ValueError( '`integrate` argument must be "trapezium" or "rectangle"' )
	initial = kwargs.pop( 'initial', 0.0 )
	return Function( *[ _DiscreteCalculusWrapper( arg, integrate=integrate, initial=initial ) for arg in pargs ], **kwargs )

def Derivative( *pargs, **kwargs ):
	"""
	DOC-TODO
	"""
	if not pargs: pargs = ( 1.0, ) 
	return Function( *[ _DiscreteCalculusWrapper( arg, integrate=False ) for arg in pargs ], **kwargs )

def ResetTimeBase( x ):
	"""
	DOC-TODO
	"""
	if isinstance( x, _DiscreteCalculusWrapper ):
		x.t_prev = None
		ResetTimeBase( x.func )
	elif isinstance( x, _SmoothingWrapper ):
		x.memory.clear()
		ResetTimeBase( x.func )
	elif isinstance( x, StateMachine ):
		raise TypeError( 'cannot call ResetTimeBase on StateMachine' )
	else:
		for mode, opfunc, term in getattr( x, 'terms', [] ): ResetTimeBase( term )

class _DiscreteCalculusWrapper( object ):
	__slots__ = [ 'func', 't_prev', 'f_prev', 'y', 'integrate' ]
	id = IDCODE
	def __init__( self, func, integrate, initial=0.0 ):
		#print( '_Accumulator.__init__(%r, %r)' % ( self, func ) )
		self.func = func
		self.t_prev = None
		self.f_prev = None
		self.integrate = integrate
		self.y = initial
		if numpy and not isinstance( initial, ( int, float, complex ) ):
			try:    self.y = numpy.array( initial, dtype=float,   copy=True )
			except: self.y = numpy.array( initial, dtype=complex, copy=True )
	def __repr__( self ): return '<%s %s>' % ( self.__class__.__name__, self.id )
	def __str__( self ): return repr( self ) + TreeBranch( self.func, last=True )
	def __call__( self, t, *pargs, **kwargs ):
		#print('%r is being called with %r, %r and %r' % ( self, t, pargs, kwargs ))
		if t is None: return self.y
		if self.t_prev is None: dt = None
		else: dt = t - self.t_prev
		self.t_prev = t
		value = self.func
		if callable( value ):
			#print( '%r is calling %r with %r, %r and %r' % ( self, value, t, pargs, kwargs ) )
			value = value( t, *pargs, **kwargs )
		if isinstance( value, Exception ): raise value
		if numpy is not None and value is not None and not isinstance( value, ( int, float, numpy.ndarray ) ):
			value = numpy.array( value, dtype=float, copy=False )
		if dt:
			if self.integrate == 'trapezium': self.y += ( value + self.f_prev ) * 0.5 * dt # adds trapezia (i.e. assume the function value climbed linearly to its current value over the interval since last call)
			elif self.integrate: self.y += value * dt # adds rectangles (i.e. assumes that the function took a step up to its current value immediately after the last call)
			else: self.y = ( value - self.f_prev ) / dt
		if dt or self.f_prev is None: self.f_prev = value
		return self.y

COS = numpy.cos if numpy else math.cos
PI  = numpy.pi  if numpy else math.pi
def RaisedCosine( x ): return 0.5 - 0.5 * COS( x * PI )

def Transition( start=0.0, end=1.0, duration=1.0, transform=None, finish=None ):
	"""
	This is a self-stopping dynamic. It uses a `Function.Watch()`
	call to ensure that, when the dynamic reaches its `end` value,
	a `Stop` exception (a subclass of `StopIteration`) is raised.
	Some frameworks (e.g. `Shady.PropertyManagement`) will
	automatically catch and deal with `StopIteration` exceptions.
	
	Args:
		start (float, int or numeric numpy.array):
			initial value
			
		end (float, int or numeric numpy.array):
			terminal value
			
		duration (float or int):
			duration of the transition, in seconds
	
		transform (callable):
			an optional single-argument function that
			takes in numeric values in the domain [0, 1]
			inclusive, and outputs numeric values. If
			you want the final output to scale correctly
			between `start` and `end`, then the output
			range of `transform` should also be [0, 1].
			
		finish (callable):
			an optional zero-argument function that
			is called when the transition terminates
			
	"""
	if numpy:
		start    = numpy.array( start,    dtype=float )
		end      = numpy.array( end,      dtype=float )
		duration = numpy.array( duration, dtype=float )
		def watch( f ):
			if numpy.all( f < 1.0 ): return
			if finish: finish()
			return f / numpy.max( f )
	else:
		def watch( f ):
			if f < 1.0: return
			if finish: finish()
			return 1.0
	p = Integral( 1.0 / duration )
	p.Watch( watch )
	if transform: p = Apply( transform, p )
	scaling = end - start
	if numpy:
		if numpy.any( scaling != 1.0 ): p *= scaling
		if numpy.any( start   != 0.0 ): p += start
	else:
		if scaling != 1.0: p *= scaling
		if start   != 0.0: p += start
	return p

Unspecified = object()
class StateMachine( object ):
	"""
	DOC-TODO
	"""
	
	class Constant( object ):
		def __init__( self, name ): self.__name = name
		def __repr__( self ): return self.__name
	
	NEXT = Constant( 'StateMachine.NEXT' )
	PENDING = Constant( 'StateMachine.PENDING' )
	CANCEL = Constant( 'StateMachine.CANCEL' )
	
	class State( object ):
		
		next = Unspecified
		duration = None
		onset = None
		offset = None
		__machine = None
		__name = None
			
		def __init__( self, name=None, duration=None, next=Unspecified, onset=None, ongoing=None, offset=None, machine=None ):
			if name     is not None: self.__name = name
			if machine  is not None: self.__machine = weakref.ref( machine )
			self.__set( duration=duration, next=next, onset=onset, ongoing=ongoing, offset=offset )
		
		def __set( self, **kwargs ):
			for attrName, value in kwargs.items():
				if value is Unspecified: continue
				if value is None and attrName != 'next': continue
				if callable( value ):
					try: inspect.getfullargspec
					except: args = inspect.getargspec( value ).args
					else:   args = inspect.getfullargspec( value ).args
					if len( args ): # this lets you set callables with either zero arguments or one argument (self) 
						if not hasattr( value, '__self__' ): value = value.__get__( self )
						if value.__self__ is not self: value = value.__func__.__get__( self )
				setattr( self, attrName, value )
		name                 = property( lambda self: self.__name if self.__name else self.__class__.__name__ )
		machine              = property( lambda self: self.__machine() )
		elapsed              = property( lambda self: self.__machine().elapsed_current )
		t                    = property( lambda self: self.__machine().t )
		fresh                = property( lambda self: self.__machine().fresh )
		Change = ChangeState = property( lambda self: self.__machine().ChangeState )
				
		def __eq__( self, other ):
			if isinstance( other, str ): return self.name.lower() == other.lower()
			else: return self is other
				
	def __init__( self, *states ):
		self.__states = {}
		self.__current = None
		self.__first_call_time = None
		self.__call_time = None
		self.__change_time = None
		self.__change_call_time = None
		self.__change_pending = []
		self.__last_added_state = None
		for arg in states:
			for state in ( arg if isinstance( arg, ( tuple, list ) ) else [ arg ] ):
				self.AddState( state )
			
	def AddState( self, name, duration=None, next=Unspecified, onset=None, ongoing=None, offset=None ):
		if isinstance( name, ( type, StateMachine.State ) ):
			state = name() if isinstance( name, type ) else name 
			if not isinstance( state, StateMachine.State ): raise TypeError( 'if you use classes to define your states, they must be subclasses of StateMachine.State' )
			StateMachine.State.__init__( state, name=None, duration=duration, next=next, onset=onset, ongoing=ongoing, offset=offset, machine=self )
		else: state = StateMachine.State( name=name,       duration=duration, next=next, onset=onset, ongoing=ongoing, offset=offset, machine=self )
		if not self.__states: self.ChangeState( state.name )
		self.__states[ state.name ] = state
		if self.__last_added_state and getattr( self.__last_added_state, 'next', Unspecified ) is Unspecified:
			self.__last_added_state.next = state.name
		self.__last_added_state = state
		return state
	
	def ChangeState( self, newState=NEXT, timeOfChange=PENDING ):
		if newState is StateMachine.NEXT:
			newState = getattr( self.__current, 'next', None )
			if newState is Unspecified: newState = None
		if timeOfChange is StateMachine.PENDING:
			self.__change_pending.append( newState )
			return StateMachine.PENDING
		if callable( newState ):
			newState = newState()
		if isinstance( newState, StateMachine.State ):
			newState = newState.name
		if newState is StateMachine.CANCEL:
			return StateMachine.CANCEL
		if newState is Unspecified: newState = None
		if newState is not None:
			newState = self.__states[ newState ]
		if not( self.__current is None and newState is None ):
			if timeOfChange is None: timeOfChange = self.__call_time
			self.__change_time = timeOfChange
			self.__change_call_time = self.__call_time
		offset = getattr( self.__current, 'offset', None )
		if callable( offset ): offset()
		self.__current = newState
		onset = getattr( self.__current, 'onset', None )
		if callable( onset ): onset()
		return newState
	
	t = property( lambda self: self.__call_time )
	state = current = property( lambda self: self.__current )	
	fresh = property( lambda self: self.__change_call_time == self.__call_time )
	elapsed_current = property( lambda self: None if ( self.__call_time is None or self.__change_time     is None ) else self.__call_time - self.__change_time )
	elapsed_total   = property( lambda self: None if ( self.__call_time is None or self.__first_call_time is None ) else self.__call_time - self.__first_call_time )
		
	def __call__( self, t ):
		if self.__call_time == t: return self.__current
			
		self.__call_time = t
		if self.__first_call_time is None:
			self.__first_call_time = self.__change_time = self.__change_call_time = t
		while self.__change_pending:
			self.ChangeState( newState=self.__change_pending.pop( 0 ), timeOfChange=t )
		
		# Note there's more than one way to change state - in descending order of recommendedness:
		# - you can rely on state.duration and state.next,
		# - or (for more dynamic behaviour) you can return a state name from state.ongoing(),
		# - or you can make an explicit call to machine.ChangeState(...) during your main loop,
		# - or you can make an explicit call to self.Change(...) during state.ongoing(), or even
		#   during state.onset() or state.offset() if you somehow absolutely must.
		# Note to maintainers: in principle you could *approximate* the function of .duration
		# and .next just by setting
		#   ongoing = lambda self: 'SomeNewState' if self.elapsed >= someDuration else None
		# but do not imagine that .duration and .next are redundant: having them as explicit
		# attributes and using the timeOfOrigin shuffle below allows transitions to be
		# performed in such a way that quantization errors in state durations do not
		# accumulate over time:
		
		while True:
			
			duration = getattr( self.__current, 'duration', None )
			if callable( duration ): duration = duration()
			if duration is not None and self.elapsed_current is not None and self.elapsed_current >= duration:
				timeOfOrigin = self.__change_time
				if timeOfOrigin is None: timeOfOrigin = self.__first_call_time
				timeOfChange = timeOfOrigin + duration
				self.ChangeState( newState=getattr( self.__current, 'next', None ), timeOfChange=timeOfChange )
	
			ongoing = getattr( self.__current, 'ongoing', None )
			if not callable( ongoing ): break
			newState = ongoing()
			if not newState: break
			if self.ChangeState( newState=newState, timeOfChange=t ) is StateMachine.CANCEL: break
			
		return self.__current

def StateMachineDemo():
	"""
	DOC-TODO
	"""
	sm = StateMachine()
	sm.AddState( 'first',  duration=123, next='second' )
	sm.AddState( 'second', duration=234, next='third' )
	sm.AddState( 'third',  duration=345, next='first' )
	import numpy; print( numpy.cumsum( [ 123, 234, 345, 123, 234, 345 ] ) )
	for t in range( 0, 1000, 2 ):
		state = sm( t )
		state = sm( t ) # it doesn't matter how many times the machine is queried with
		                # the same t: the change happens only once, and "fresh"-ness
		                # of the state persists until called with a different t
		if state.fresh:
			if state == 'first': print( 'passing GO, collecting $200' )
			print( '%5g: %s (elapsed = %r)' % ( t, state.name, state.elapsed ) )

if __name__ == '__main__':
	p = Apply( numpy.sin, Integral( Integral( 0.05 ) ) + [ numpy.pi / 2, 0] ) * 500
	
	print( p )
	print( p(0) )
	print( p(1) )
	print( p(2) )

