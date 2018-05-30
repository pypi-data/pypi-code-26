import numpy as np

_iinfo = np.iinfo(int)

@profile
def timestep(t, dt):
    elapsed_steps = t/dt + 1e-3
    if np.isscalar(elapsed_steps) or elapsed_steps.shape == ():
        if np.isinf(elapsed_steps):
            if elapsed_steps > 0:
                return _iinfo.max
            else:
                return _iinfo.min
        else:
            return np.int_(elapsed_steps)
    else:
        int_steps = np.asarray(elapsed_steps, dtype=int)
        are_inf, = np.nonzero(np.isinf(elapsed_steps))
        int_steps[are_inf] = np.where(int_steps[are_inf] > 0,
                                      _iinfo.max/2, _iinfo.min/2)
        return int_steps

X = np.random.rand(1000000)
dt = 0.0001
timestep(X, dt)
