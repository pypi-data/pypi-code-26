from brian2 import NeuronGroup, StateMonitor, run, ms, figure, plot, show

neurons = NeuronGroup(10, model="v:1")
neurons[0:5].v = 1
neurons[0:5].run_regularly("v += 1", dt=10 * ms)
print neurons.contained_objects
statemon = StateMonitor(neurons, variables=["v"], record=True)

run(100 * ms)

print(neurons[0:5].v)

fig = figure()
plot(statemon.t / ms, statemon.v.T)
show()
