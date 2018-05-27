import numpy as np

from .control import model_setup
from .cp_confocal import twod
from .cp_triplet import trip
from .cp_mix import double_pnum


# 2D + 2D + Triplet Gauß
    # Model 6031
def CF_Gxyz_gauss_2D2DT(parms, tau):
    u""" Two-component, two-dimensional diffusion with a Gaussian laser
        profile, including a triplet component.
        The triplet factor takes into account blinking according to triplet
        states of excited molecules.
        Set *T* or *τ_trip* to 0, if no triplet component is wanted.

        particle1 = F₁/(1+τ/τ₁)
        particle2 = α²*(1-F₁)/(1+τ/τ₂)
        triplet = 1 + T/(1-T)*exp(-τ/τ_trip)
        norm = (F₁ + α*(1-F₁))²
        G = 1/n*(particle1 + particle2)*triplet/norm + offset

        *parms* - a list of parameters.
        Parameters (parms[i]):
        [0] n       Effective number of particles in confocal area
                    (n = n₁+n₂)
        [1] τ₁      Diffusion time of particle species 1
        [2] τ₂      Diffusion time of particle species 2
        [3] F₁      Fraction of molecules of species 1 (n₁ = n*F₁)
                    0 <= F₁ <= 1
        [4] α       Relative molecular brightness of particle 2
                    compared to particle 1 (α = q₂/q₁)
        [5] τ_trip  Characteristic residence time in triplet state
        [6] T       Fraction of particles in triplet (non-fluorescent)
                    state 0 <= T < 1
        [7] offset
        *tau* - lag time
    """
    n=parms[0]
    taud1=parms[1]
    taud2=parms[2]
    F=parms[3]
    alpha=parms[4]
    tautrip=parms[5]
    T=parms[6]
    off=parms[7]

    g = double_pnum(n=n,
                    F1=F,
                    alpha=alpha,
                    comp1=twod,
                    comp2=twod,
                    kwargs1={"tau":tau,
                             "taudiff":taud1},
                    kwargs2={"tau":tau,
                             "taudiff":taud2},
                    )

    tr = trip(tau=tau, T=T, tautrip=tautrip)

    G = off + g*tr
    return G


def supplements(parms, countrate=None):
    u"""Supplementary parameters:
        [8] n₁ = n*F₁     Particle number of species 1
        [9] n₂ = n*(1-F₁) Particle number of species 2
    """
    # We can only give you the effective particle number
    n = parms[0]
    F1 = parms[3]
    Info = list()
    # The enumeration of these parameters is very important for
    # plotting the normalized curve. Countrate must come out last!
    Info.append([u"n\u2081", n*F1])
    Info.append([u"n\u2082", n*(1.-F1)])
    if countrate is not None:
        # CPP
        cpp = countrate/n
        Info.append(["cpp [kHz]", cpp])
    return Info


parms = [
            25,      # n
            5,       # taud1
            1000,    # taud2
            0.5,     # F
            1.0,     # alpha
            0.001,   # tautrip
            0.01,    # T
            0.0      # offset
            ] 

## Boundaries
# strictly positive
boundaries = [[0, np.inf]]*len(parms)
# F
boundaries[3] = [0,.9999999999999]
# T
boundaries[6] = [0,.9999999999999]
boundaries[-1] = [-np.inf, np.inf]


model_setup(
             modelid=6031,
             name="Separate 2D diffusion with triplet (confocal)",
             comp="T+2D+2D",
             mtype="Confocal (Gaussian) and triplet",
             fctn=CF_Gxyz_gauss_2D2DT,
             par_labels=[
                            u"n",
                            u"τ"+u"\u2081"+u" [ms]",
                            u"τ"+u"\u2082"+u" [ms]",
                            u"F"+u"\u2081", 
                            u"\u03b1"+u" (q"+u"\u2082"+"/q"+u"\u2081"+")", 
                            u"τ_trip [ms]",
                            u"T",
                            u"offset"
                            ],
             par_values=parms,
             par_vary=[True, True, True, True, False, False, False, False],
             par_boundaries=boundaries,
             par_constraints=[[2, ">", 1], [5, "<", 1]],
             par_hr_labels=[
                            u"n",
                            u"τ"+u"\u2081"+u" [ms]",
                            u"τ"+u"\u2082"+u" [ms]",
                            u"F"+u"\u2081", 
                            u"\u03b1"+" (q"+u"\u2082"+"/q"+u"\u2081"+")", 
                            u"τ_trip [µs]",
                            u"T",
                            u"offset"
                            ],
             par_hr_factors=[
                            1.,     # "n",
                            1.,     # "τ"+u"\u2081"+" [ms]",
                            1.,     # "τ"+u"\u2082"+" [ms]",
                            1.,     # "F"+u"\u2081", 
                            1.,     # u"\u03b1"+" (q"+u"\u2082"+"/q"+u"\u2081"+")", 
                            1000.,  # "τ_trip [µs]",
                            1.,     # "T",
                            1.      # "offset"
                            ],
             supplementary_method=supplements
            )
