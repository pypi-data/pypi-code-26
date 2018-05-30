def compute_total_impulse(spin_rate, roll_inertia, radial_distance):
    """Computes total impulse required to spin rocket at desired rate.

    Args:
        spin_rate (int, float): Desired roll spin rate in rad/s of launch vehicle
        for stabilization.
        roll_inertia (int, float): The roll inertia of the launch vehicle in kg-m^2.
        radial_distance (int, float): The location of the solid rocket motors radially
        along the launch vehicle in m.

    Returns:
        total_impulse (float): The total impulse in N-s required to spin the launch
        vehicle to the desired rate.

    """
    if spin_rate <= 0 or roll_inertia <= 0 or radial_distance <= 0:
        raise ValueError('Spin rate, roll inertia, and radial distance must be positive values.')
    total_impulse = roll_inertia*spin_rate/float(radial_distance)
    return total_impulse
    
def compute_impulse_per_motor(total_impulse):
    """Computes impulse per motor (set of 2) required to spin rocket at desired rate.
    
    Args:
        total_impulse (int, float): Total impulse computed from the compute_total_impulse
        function (N-s).

    Returns:
        (float): The impulse of a single motor (from a pair) to spin a launch vehicle
        at a particular spin rate.

    """
    if total_impulse <= 0:
        raise ValueError('Total impulse must be a positive value.')
    return total_impulse/2.0