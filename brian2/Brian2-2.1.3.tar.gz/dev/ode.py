from brian2 import *
from brian2.core.variables import Variables

prefs.codegen.target = 'cython'

G = NeuronGroup(2, '''v : volt
                      v0 : volt''')
tau = 10*ms
runner = G.run_regularly('_v_diff =  (_gsl_v0 - _gsl_v) / tau')
runner.variables = Variables(runner)
for var in ['v', 'v0']:
    long_name = '_gsl_'+var
    runner.variables.add_auxiliary_variable(long_name, dimensions=G.variables[var].dim,
                                            scalar=G.variables[var].scalar)
run(0*ms)
print runner.codeobj.code
