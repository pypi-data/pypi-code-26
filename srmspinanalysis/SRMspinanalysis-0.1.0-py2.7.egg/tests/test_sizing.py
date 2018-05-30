from .. import sizing
import numpy as np

def test_compute_total_impulse_1():
    spin_rate = 25.0
    roll_inertia = 1.0
    radial_distance = 0.175
    # Computed by hand
    exp = 142.857
    obs = sizing.compute_total_impulse(spin_rate, roll_inertia, radial_distance)
    assert np.allclose(exp, obs)
    
def test_compute_total_impulse_2():
    spin_rate = 1.0
    roll_inertia = 1.0
    radial_distance = 1.0
    # Computed by hand
    exp = 1.0
    obs = sizing.compute_total_impulse(spin_rate, roll_inertia, radial_distance)
    assert np.allclose(exp, obs)