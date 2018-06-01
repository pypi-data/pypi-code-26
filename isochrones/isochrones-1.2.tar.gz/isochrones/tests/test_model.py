import tempfile
import os, shutil, glob
import logging

import numpy as np
from isochrones.dartmouth import Dartmouth_Isochrone
from isochrones.mist import MIST_Isochrone
from isochrones import StarModel, get_ichrone

import pickle

DAR = Dartmouth_Isochrone()
MIST = MIST_Isochrone()

props = dict(Teff=(5800, 100), logg=(4.5, 0.1),
             B=(5.7,0.05), V=(5.0, 0.05))


tempdir = tempfile.gettempdir()


def test_pickle():
    _check_pickle(DAR)
    _check_pickle(MIST)

def test_emcee_p0():
    _check_emcee_p0(DAR)
    _check_emcee_p0(MIST)

def _get_model(ic, props=props):
    return StarModel(ic, **props)

def _check_pickle(ic, props=props):
    mod = _get_model(ic, props=props)

    testfile = os.path.join(tempdir, 'test.pkl')
    with open(testfile, 'wb') as fout:
        pickle.dump(mod, fout)

    with open(testfile, 'rb') as fin:
        mod = pickle.load(fin)


def _check_emcee_p0(ic, props=props):
    mod = _get_model(ic, props=props)
    p0 = mod.emcee_p0(200)
    nbad = 0
    for i,p in enumerate(p0):
        if not np.isfinite(mod.lnpost(p)):
            print(p)
            nbad += 1

    assert nbad==0
