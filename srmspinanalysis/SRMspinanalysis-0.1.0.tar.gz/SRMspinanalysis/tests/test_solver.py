from .. import solver
import numpy as np

def test_compute_moments_1():
    params = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    thrust_motor_1 = 25.0
    thrust_motor_2 = 6.0
    # Computed by hand
    exp = np.array([0.0, 51.0, 37.0])
    obs = solver.compute_moments(params, thrust_motor_1, thrust_motor_2)
    assert np.allclose(exp, obs)
    
def test_interpolate_thrust_data_1():
    t_desired = 2.5
    time = np.array([2,3,4,5])
    thrust = np.array([4,5,6,7])
    interp_thrust = solver.interpolate_thrust_data(t_desired, time, thrust)
    exp = 4.5
    assert np.allclose(exp, interp_thrust)
    
def test_interpolate_thrust_data_2():
    t_desired = 1
    time = np.array([2,3,4,5])
    thrust = np.array([4,5,6,7])
    interp_thrust = solver.interpolate_thrust_data(t_desired, time, thrust)
    exp = 0.0
    assert np.allclose(exp, interp_thrust)

def test_interpolate_thrust_data_3():
    t_desired = 6
    time = np.array([2,3,4,5])
    thrust = np.array([4,5,6,7])
    interp_thrust = solver.interpolate_thrust_data(t_desired, time, thrust)
    exp = 0.0
    assert np.allclose(exp, interp_thrust)