import numpy as np
from envmap import EnvironmentMap
from pyshtools.shtools import SHExpandDH, MakeGridDH

from spharm import FSHT, iFSHT, sphericalHarmonicTransform, inverseSphericalHarmonicTransform



if __name__ == '__main__':
    from matplotlib import pyplot as plt

    e = EnvironmentMap('envmap.exr', 'angular')
    e.resize((64, 64))
    e.convertTo('latlong')

    # P, nodes = _getP(e, 15)
    # refP = _getRefP(np.cos(nodes), 15)

    # for i in range(P.shape[1] - 5, P.shape[1]):
    #     plt.plot(np.linspace(-1, 1, P.shape[0]), P[:,i], label="{}".format(i))
    #     plt.plot(np.linspace(-1, 1, P.shape[0]), refP[:,i], label="ref{}".format(i))
    # plt.legend();
    # plt.show()

    # import pdb; pdb.set_trace()

    sh_degree = 10
    topo = e.data.copy()
    topo_rec = np.zeros((64, 128, 3))
    for i in range(3):
        coeffs = SHExpandDH(topo[:, :, i], sampling=2, lmax_calc=sh_degree)
        topo_rec[:, :, i] = MakeGridDH(coeffs, lmax=31, sampling=2, lmax_calc=sh_degree)
    topo_rec = np.clip(topo_rec, a_min=0, a_max=None)

    coeffs_fsht = FSHT(e.copy(), 10)
    #coeffs = sphericalHarmonicTransform(e, 10)

    err_f = []
    err = []
    for degrees in [10]:
        db_coef = int((2*(degrees + 1)+1)**2/8)
        er_fsht = iFSHT(coeffs_fsht[:db_coef,:], 64)
        err_f.append(np.sum((er_fsht.data*0.029 - e.data)**2))
        #er = inverseSphericalHarmonicTransform(coeffs[:db_coef,:], 256)
        #err.append(np.sum((er.data - e.data)**2))

    fr = er_fsht.data * 0.5
    plt.subplot(2,2,1); plt.imshow(np.clip(e.data, 0, 1))
    #plt.subplot(2,2,2); plt.imshow(np.clip(er.data, 0, 1))
    plt.subplot(2,2,2); plt.imshow(np.clip(fr[:,:,0] / topo_rec[:,:,0], -1, 10)); plt.colorbar()
    plt.subplot(2,2,3); plt.imshow(np.clip(fr, 0, 1))
    plt.subplot(2,2,4); plt.imshow(np.clip(topo_rec, 0, 1))
    plt.show()

