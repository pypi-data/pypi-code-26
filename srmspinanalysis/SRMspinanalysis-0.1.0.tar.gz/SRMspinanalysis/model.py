import numpy as np

class RocketModel():
    """Rocket model includes physical characteristics of launch vehicle.

    Attributes
    ----------
    r1 : Radial location of solid rocket motor for spin-up [m]
    r2 : Radial location of solid rocket motor for spin-up [m]
    d1 : Longitudinal location of solid rocket motor for spin-up [m]
    d2 : Longitudinal location of solid rocket motor for spin-up [m]
    Ixx : Roll inertia of rocket [kg-m^2]
    Iyy : Yaw inertia of rocket [kg-m^2]
    Izz : Pitch inertia of rocket [kg-m^2]
    
    """
    
    def __init__(self, r1=4.5*0.0254, r2=4.5*0.0254,
                       d1=25.0*0.0254, d2=25.0*0.0254,
                       Ixx=185000.0*0.45359237*0.0254**2,
                       Iyy=185000.0*0.45359237*0.0254**2,
                       Izz=3500.0*0.45359237*0.0254**2,):
        """Initalizes the rocket model with user defined values.
        """
        self.r1 = r1 # m
        self.r2 = r2 # m
        self.d1 = d1 # m
        self.d2 = d2 # m
        self.Ixx = Ixx # kg-m^2
        self.Iyy = Iyy # kg-m^2
        self.Izz = Izz # kg-m^2
        
    def create_design_params(self):
        """Packages the design parameters into a numpy array.
        """
        return np.array([self.r1, self.r2, self.d1, self.d2, self.Ixx, self.Iyy, self.Izz])