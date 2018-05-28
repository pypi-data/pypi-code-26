from .units import UnitsProxy, Pint

units = UnitsProxy()
units.engine = Pint
del UnitsProxy
