from brian2 import *

prefs.codegen.target = 'cython'

G = NeuronGroup(1, '''v : 1
                      c : integer (constant)''')
G.run_regularly('''x = i
                   y = x
                   v = y''')
run(defaultclock.dt)
