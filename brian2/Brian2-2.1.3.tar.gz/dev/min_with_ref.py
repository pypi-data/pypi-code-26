from brian2 import *
prefs.codegen.target = 'cython'
group = NeuronGroup(1, 'dv/dt = -v/(10*ms) : 1', method='euler', refractory=1*ms, threshold='False')
run(0*ms)
