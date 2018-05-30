# Helper functions for geometric calculations in 3D

import numpy as np

# convenience functions for math in degrees
cos_d = lambda x: np.cos(np.deg2rad(x))
sin_d = lambda x: np.sin(np.deg2rad(x))

def rot_matrix_x(rot_angle):
    """ Return a rotation matrix for a rotation around the X axis.

    Parameters
    -----------
    rot_angle : float
        Rotation angle, in degrees

    Returns
    ---------
    rotmat : numpy.matrix
        Rotation matrix
    """
    return np.matrix([[1,                0,                0],
                     [0, cos_d(rot_angle), -sin_d(rot_angle)], \
                     [0, sin_d(rot_angle),  cos_d(rot_angle)]])

def rot_matrix_y(rot_angle):
    """ Return a rotation matrix for a rotation around the Y axis.

    Parameters and Returns same as RotX
    """
    return np.matrix([[cos_d(rot_angle), 0, sin_d(rot_angle)],
                     [0,                1,          0       ],
                     [-sin_d(rot_angle),0, cos_d(rot_angle)]])

def rot_matrix_z(rot_angle):
    """ Return a rotation matrix for a rotation around the Z axis.

    Parameters and Returns same as RotX
    """
    return np.matrix([[cos_d(rot_angle),-sin_d(rot_angle), 0],
                     [sin_d(rot_angle),  cos_d(rot_angle),0],
                     [0,                0,                1]])


