from brian2 import *
# from CondSornB2Par import *
from matplotlib.pyplot import *
import pdb

### Neuron model
#
# We use a noisy conductance based model with excitatory / ampa and inhibitory /
#  gaba conductances as well as additional variables to permit implementation of
#  synaptic normalization and intrinsic firing threshold plasticity (not yet
#  implemented).
#
c = 1*nF
g_leak = 10*nS
e_gaba = -70*mV
e_ampa = 0*mV
tau_gaba = 5*ms
tau_ampa = 5*ms
v_rest = -70*mV
s_n = 1*mV
taupre = taupost = 10*ms
dwpre = 1*nS
dwpost = 1*nS
w_max = 10*nS
eqs_neuron = '''
dv/dt=(g_leak*(v_rest-v)+i_ext+i_syn)/c+s_n*xi*tau_n**-0.5: volt  # voltage
i_ext : amp  # external current
i_syn=g_ampa*(e_ampa-v)+g_gaba*(e_gaba-v) : amp  # synaptic current
dg_ampa/dt=-g_ampa/tau_ampa : siemens  # ampa synaptic conductance
sumw_ampa : siemens  # total ampa input
sumw_ampa_target : siemens  # target total ampa input
dg_gaba/dt=-g_gaba/tau_gaba : siemens  # gaba synaptic conductance
sumw_gaba : siemens  # toal gaba conductance
sumw_gaba_target : siemens  # target total gaba input
v_t : volt  # firing threshold
refrac : second  # refractory period
'''

### Synapse model
#
# We use conductance based STDP ampa synapses and conductance based gaba synapses
#  with additional variables for synaptic normalization (not yet implemented).
#
ampa_model_eq = '''
w_ampa : siemens  # synaptic weight (ampa synapse)
dwpre/dt=-wpre/taupre : siemens (event-driven)
dwpost/dt=-wpost/taupost : siemens (event-driven)
sumw_ampa_post = w_ampa : siemens (summed)
'''
gaba_model_eq = '''
w_gaba : siemens  # synaptic weight (gaba synapse)
sumw_gaba_post = w_gaba : siemens (summed)
'''
ampa_pre_eq = '''
g_ampa_post+=w_ampa  # increment ampa conductance
wpre+=dwpre
w_ampa=clip(w_ampa+wpost,0,w_max)  # hard boundaries
'''
simple_ampa_pre_eq = '''
g_ampa_post+=w_ampa  # increment ampa conductance
'''
gaba_pre_eq = '''
g_gaba_post+=w_gaba  # increment gaba conductance
'''
ampa_post_eq = '''
wpost+=dwpost
w_ampa=clip(w_ampa+wpre,0,w_max)  # hard boundaries
'''

### Network model
#
# We base the network design on the network described in Miner and Triesch PLOS
#  CB 2016, minus the spatial topology.
#
reset_eqs = '''
v=v_rest  # reset to resting potential upon spike
'''
n_e = n_i = 1
# neurons=NeuronGroup(n_e+n_i,eqs_neuron,threshold=thr_eqs,reset=reset_eqs)
neurons = NeuronGroup(n_e + n_i, eqs_neuron, threshold='v>v_t', reset=reset_eqs,
                      refractory='refrac')
nrns_e = neurons[:n_e]  # excitatory subgroup
nrns_i = neurons[n_e:]  # inhibitory subgroup
syn_ee = Synapses(nrns_e, nrns_e, model=ampa_model_eq,
                  on_pre=ampa_pre_eq,
                  on_post=ampa_post_eq)  # create e->e synapses
syn_ee.connect(condition='i!=j', p=.1)  # connect e->e synapses
syn_ei = Synapses(nrns_e, nrns_i, model=ampa_model_eq,
                  on_pre=simple_ampa_pre_eq)  # create e->i synapses
syn_ei.connect(p=0.1)  # connect e->i synapses
syn_ie = Synapses(nrns_i, nrns_e, model=gaba_model_eq,
                  on_pre=gaba_pre_eq)  # create i->e synapses
syn_ie.connect(p=0.1)  # connect i->e synapses
syn_ii = Synapses(nrns_i, nrns_i, model=gaba_model_eq,
                  on_pre=gaba_pre_eq)  # create i->i synapses
syn_ii.connect(condition='i!=j', p=.1)  # connect i->i synapses
tau_n = 10*ms
run(0*ms)