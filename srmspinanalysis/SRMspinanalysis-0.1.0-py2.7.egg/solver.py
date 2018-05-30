import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import get_data
import model
import plot

def compute_moments(design_params, thrust_motor_1, thrust_motor_2):
    """Computes moment vector given thrust information from each motor and
    specific design parameters.

    Args:
        design_params (np.array()): Array of design parameters.
        [r1, r2, d1, d2, Ixx, Iyy, Izz] where r1 and r2 are the radial locations of
        the solid rocket motors (m), d1 and d2 are the longitudinal locations of the two
        motors (m), and Ixx, Iyy, and Izz are the interia values (kg-m^2).
        thrust_motor_1 (float): Thrust from motor 1 (N).
        thrust_motor_2 (float): Thrust from motor 2 (N).

    Returns:
        moments (np.array()): Moment vector in the x, y, and z directions (N-m).
    
    """
    r1, r2, d1, d2, Ixx, Iyy, Izz = design_params
    if (design_params >= 0).all():
        Mx = 0.0;
        My = thrust_motor_1*d1 - thrust_motor_2*d2
        Mz = thrust_motor_1*r1 + thrust_motor_2*r2
        moments = np.array([Mx, My, Mz])
        return moments
    else:
        raise ValueError('All design parameters should be positive values.')

def interpolate_thrust_data(t, motor_time_data, motor_thrust_data):
    """Performs a linear interpolation on motor thrust data and extracts the value
    at a desired time.

    Args:
        t (float): Desired time (s) at which to compute thrust.
        motor_time_data (np.array()): Time data from a specific motor (s).
        motor_thrust_data (np.array()): Thrust data from a specific motor (N).

    Returns:
        (float): Thrust at the specified time t.

    """
    if t < np.min(motor_time_data) or t > np.max(motor_time_data):
        return 0.0
    else:
        interp_thrust = interp1d(motor_time_data, motor_thrust_data)
        return interp_thrust(t).item()

def euler_eom(f, t, design_params, SRM1, SRM2):
    """Numerically computes the time derivatives of the specified function variables.
    To be used for numerical integration.

    Args:
        f (np.array()): Array of variables to be numerically solved.
        [wx, wy, wz, psi, theta, phi] where wx, wy, wz are the body angles of the launch
        vehicle (rad) and psi, theta, and phi are the Eulerian angles (rad).
        t (float): Time (s) to numerically solve equations of motion.
        design_params (np.array()): Array of design parameters.
        [r1, r2, d1, d2, Ixx, Iyy, Izz] where r1 and r2 are the radial locations of
        the solid rocket motors (m), d1 and d2 are the longitudinal locations of the two
        motors (m), and Ixx, Iyy, and Izz are the interia values (kg-m^2).
        SRM1 (SolidRocketMotor()): First solid rocket motor organized into a class.
        SRM2 (SolidRocketMotor()): Second solid rocket motor organized into a class.

    Returns:
        (np.array()): Array of the time derivatives of the function variables f.

    """
    wx, wy, wz, psi, theta, phi = f
    r1, r2, d1, d2, Ixx, Iyy, Izz = design_params
    thrust_motor_1 = interpolate_thrust_data(t, SRM1.motor_time_data, SRM1.motor_thrust_data)
    thrust_motor_2 = interpolate_thrust_data(t, SRM2.motor_time_data, SRM2.motor_thrust_data)
    moments = compute_moments(design_params, thrust_motor_1, thrust_motor_2)
    Mx, My, Mz = moments
    # Differential equations of motion
    wx_dot = (Mx - (Izz - Iyy) * wy * wz) / Ixx
    wy_dot = (My - (Ixx - Izz) * wz * wx) / Iyy
    wz_dot = (Mz - (Iyy - Ixx) * wx * wy) / Izz
    psi_dot = (wy * np.sin(phi) + wz * np.cos(phi)) * 1.0 / np.cos(theta)
    theta_dot = wy * np.cos(phi) - wz * np.sin(phi)
    phi_dot = wx + (wy * np.sin(phi) + wz * np.cos(phi)) * np.tan(theta)
    return np.array([wx_dot, wy_dot, wz_dot, psi_dot, theta_dot, phi_dot])

def integrate_eom(initial_conditions, t_span, design_params, SRM1, SRM2):
    """Numerically integrates the zero gravity equations of motion.

    Args:
        initial_conditions (np.array()): Array of initial conditions. Typically set
        to an array of zeros.
        t_span (np.array()): Time vector (s) over which to integrate the equations 
        of motions.
        design_params (np.array()): Array of design parameters.
        [r1, r2, d1, d2, Ixx, Iyy, Izz] where r1 and r2 are the radial locations of
        the solid rocket motors (m), d1 and d2 are the longitudinal locations of the two
        motors (m), and Ixx, Iyy, and Izz are the interia values (kg-m^2).
        SRM1 (SolidRocketMotor()): First solid rocket motor organized into a class.
        SRM2 (SolidRocketMotor()): Second solid rocket motor organized into a class.

    Returns:
        (np.array()): Numerical solutions for wx, wy, wz, psi, theta, and phi.

    """
    return odeint(euler_eom, ic, t, args=(design_params, SRM1, SRM2))

def compute_nutation_angle(theta, phi):
    """Computes nutation angle of launch vehicle in degrees.

    Args:
        theta (np.array()): Array of Euler angle theta values (rad).
        phi (np.array()): Array of Euler angle phi values (rad).

    Returns:
        (np.array()): Array of nutation angle values (rad).

    """
    nutation_angle = np.arccos(np.multiply(np.cos(theta),np.cos(phi)))
    return nutation_angle * (180.0 / np.pi)
    
def compute_precession_angle(theta, psi):
    """Computes precession angle of launch vehicle in degrees.

    Args:
        theta (np.array()): Array of Euler angle theta values (rad).
        psi (np.array()): Array of Euler angle psi values (rad).

    Returns:
        (np.array()): Array of precession angle values (rad).

    """
    precession_angle = np.arccos(np.multiply(np.cos(theta),np.cos(psi)))
    return precession_angle * (180.0 / np.pi)

# Need to add tests for euler_eom, integrate_eom, compute_nutation_angle, compute_precession_angle.

if __name__ == '__main__':
    url = 'http://www.thrustcurve.org/simfilesearch.jsp?id=51'
    ic = np.zeros(6)
    tstart = 0.0
    tend = 7.0
    dt = 0.0001
    delay = 0.02
    t = np.linspace(tstart, tend, tend/dt)
    RocketModel = model.RocketModel()
    design_params = RocketModel.create_design_params()
    SRM1 = get_data.SolidRocketMotor(url)
    SRM2 = get_data.SolidRocketMotor(url)
    SRM1.motor_number_of_grains = 3.0
    SRM2.motor_number_of_grains = 3.0
    SRM2.add_delay(delay)
    SRM1.motor_thrust_data = SRM1.compute_thrust_per_grain() # I200 have three grains.
    SRM2.motor_thrust_data = SRM2.compute_thrust_per_grain() # I200 have three grains.
    wx, wy, wz, psi, theta, phi = integrate_eom(ic, t, design_params, SRM1, SRM2).T
    nutation_angle = compute_nutation_angle(theta, phi)
    precession_angle = compute_precession_angle(theta, psi)
    #plot.plot_all(t, psi, theta, phi, nutation_angle, precession_angle)