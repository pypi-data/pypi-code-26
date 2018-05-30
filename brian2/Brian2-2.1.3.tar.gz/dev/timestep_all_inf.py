import numpy as np

_infinity_int = np.iinfo(int).max//2

def timestep(t, dt):
    elapsed_steps = t/dt + 1e-3
    if np.isscalar(elapsed_steps) or elapsed_steps.shape == ():
        if np.isinf(elapsed_steps):
            if elapsed_steps > 0:
                return _infinity_int
            else:
                return -_infinity_int
        else:
            return np.int_(elapsed_steps)
    else:
        int_steps = np.asarray(elapsed_steps, dtype=int)
        are_inf, = np.nonzero(np.isinf(elapsed_steps))
        int_steps[are_inf] = np.where(int_steps[are_inf] > 0,
                                      _infinity_int, -_infinity_int)
        return int_steps

X = np.full(1000000, np.inf)
dt = 0.0001
timestep(X, dt)
