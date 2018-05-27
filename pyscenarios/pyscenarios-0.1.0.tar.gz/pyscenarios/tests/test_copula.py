import pytest
import numpy as np
import scipy.stats
from numpy.testing import assert_allclose
from pyscenarios.copula import gaussian_copula, t_copula
from pyscenarios.stats import tail_dependence


cov = [[1.0, 0.9, 0.7],
       [0.9, 1.0, 0.4],
       [0.7, 0.4, 1.0]]


def test_gaussian_mersenne_np():
    actual = gaussian_copula(cov, samples=4, seed=123, chunks=None,
                             rng='Mersenne Twister')
    expect = [[-1.08563060, -0.54233474, -1.15002017],
              [-1.50629471, -1.60787125,  0.04561073],  # noqa
              [-2.42667924, -2.37097000, -0.86315499],
              [-0.86674040, -1.07598597, -0.29407627]]
    assert_allclose(expect, actual, 1e-6, 0)
    assert isinstance(actual, np.ndarray)


def test_gaussian_mersenne_da():
    actual = gaussian_copula(cov, samples=4, seed=123, chunks=2,
                             rng='Mersenne Twister')
    expect = [[ 1.61739599,  1.34668479,  0.85965138],  # noqa
              [ 0.00936110,  0.77307164, -0.65639660],  # noqa
              [-0.88414686, -1.07582330, -0.47076357],
              [-1.63883139, -1.21794817, -1.47348213]]
    assert_allclose(expect, actual, 1e-6, 0)
    assert actual.chunks == ((2, 2), (2, 1))


@pytest.mark.parametrize('chunks,expect_chunks', [
    (None, None),
    (2, ((2, 2), (2, 1))),
    (((3, 1), (2, 1)), ((3, 1), (2, 1))),
])
def test_gaussian_sobol(chunks, expect_chunks):
    actual = gaussian_copula(cov, samples=4, seed=123, chunks=chunks,
                             rng='SOBOL')
    expect = [[ 0.        ,  0.        ,  0.        ],  # noqa
              [-0.67448975, -0.31303751, -1.15262386],
              [ 0.67448975,  0.31303751,  1.15262386],  # noqa
              [ 0.31863936,  0.78820110, -0.53727912]]  # noqa
    assert_allclose(expect, actual, 1e-6, 0)
    if chunks:
        assert actual.chunks == expect_chunks
    else:
        assert isinstance(actual, np.ndarray)


def test_student_t_mersenne_np():
    actual = t_copula(cov, df=3, samples=4, seed=123, chunks=None,
                      rng='Mersenne Twister')
    expect = [[-1.48810072, -0.86441534, -1.54668921],
              [-1.29120595, -1.35445918,  0.04614266],  # noqa
              [-1.69841381, -1.67427423, -0.76713426],
              [-0.52427748, -0.64222262, -0.18205599]]
    assert_allclose(expect, actual, 1e-6, 0)
    assert isinstance(actual, np.ndarray)


def test_student_t_mersenne_da():
    actual = t_copula(cov, df=3, samples=4, seed=123, chunks=2,
                      rng='Mersenne Twister')
    expect = [[ 0.9251499 ,  0.78838765,  0.52075254],  # noqa
              [ 0.00733126,  0.58581369, -0.50181461],  # noqa
              [-0.46342698, -0.55862319, -0.25037537],
              [-0.92150594, -0.70869994, -0.84036731]]
    assert_allclose(expect, actual, 1e-6, 0)
    assert actual.chunks == ((2, 2), (2, 1))


@pytest.mark.parametrize('chunks,expect_chunks', [
    (None, None),
    (2, ((2, 2), (2, 1))),
    (((3, 1), (2, 1)), ((3, 1), (2, 1))),
])
def test_student_t_sobol(chunks, expect_chunks):
    actual = t_copula(cov, df=3, samples=4, seed=123, chunks=chunks,
                      rng='SOBOL')
    expect = [[ 0.        ,  0.        ,  0.        ],  # noqa
              [-0.90292647, -0.44513114, -1.38033019],
              [ 0.51756147,  0.24504617,  0.84650386],  # noqa
              [ 0.59093028,  1.28328308, -0.94456215]]  # noqa
    assert_allclose(expect, actual, 1e-6, 0)
    if chunks:
        assert actual.chunks == expect_chunks
    else:
        assert isinstance(actual, np.ndarray)


def test_it_mersenne_np():
    actual = t_copula(cov, df=[3, 4, 5], samples=4, seed=123, chunks=None,
                      rng='Mersenne Twister')
    expect = [[-1.48810072, -0.80579141, -1.48680149],
              [-1.29120595, -1.40226642,  0.04565698],  # noqa
              [-1.69841381, -1.77537961, -0.79048734],
              [-0.52427748, -0.68508399, -0.20095568]]
    assert_allclose(expect, actual, 1e-6, 0)
    assert isinstance(actual, np.ndarray)


def test_it_mersenne_da():
    actual = t_copula(cov, df=[3, 4, 5], samples=4, seed=123,
                      chunks=2, rng='Mersenne Twister')
    expect = [[ 0.92514990,  0.84367196,  0.57859631],  # noqa
              [ 0.00733126,  0.60760124, -0.53208793],  # noqa
              [-0.46342698, -0.60402557, -0.28417274],
              [-0.92150594, -0.75838980, -0.94757843]]
    assert_allclose(expect, actual, 1e-6, 0)
    assert actual.chunks == ((2, 2), (2, 1))


@pytest.mark.parametrize('chunks,expect_chunks', [
    (None, None),
    (2, ((2, 2), (2, 1))),
    (((3, 1), (2, 1)), ((3, 1), (2, 1))),
])
def test_it_sobol(chunks, expect_chunks):
    actual = t_copula(cov, df=[3, 4, 5], samples=4, seed=123,
                      chunks=chunks, rng='SOBOL')
    expect = [[ 0.        ,  0.        ,  0.        ],  # noqa
              [-0.90292647, -0.41928686, -1.35361744],
              [ 0.51756147,  0.25248047,  0.91032037],  # noqa
              [ 0.59093028,  1.20943444, -0.81940488]]  # noqa
    assert_allclose(expect, actual, 1e-6, 0)
    if chunks:
        assert actual.chunks == expect_chunks
    else:
        assert isinstance(actual, np.ndarray)


all_copulas = pytest.mark.parametrize(
    'func,kwargs', [
        (gaussian_copula, {'rng': 'Mersenne Twister'}),
        (gaussian_copula, {'rng': 'Mersenne Twister', 'chunks': (4096, 2)}),
        (gaussian_copula, {'rng': 'SOBOL'}),
        (t_copula, {'df': 8, 'rng': 'Mersenne Twister'}),
        (t_copula, {'df': 8, 'rng': 'Mersenne Twister', 'chunks': (4096, 2)}),
        (t_copula, {'df': 8, 'rng': 'SOBOL'}),
        (t_copula, {'df': [8, 9, 10], 'rng': 'Mersenne Twister'}),
        (t_copula, {'df': [8, 9, 10], 'rng': 'Mersenne Twister',
                    'chunks': (4096, 2)}),
        (t_copula, {'df': [8, 9, 10], 'rng': 'SOBOL'}),
    ])


@all_copulas
def test_normal_01(func, kwargs):
    """All copulas produce normal (0, 1) distributions for all series
    """
    s = func(cov, samples=65535, **kwargs)
    s = scipy.stats.norm.cdf(s)
    hist, bin_edges = np.histogram(s)

    assert_allclose(hist / 65535, [.3] * 10, rtol=0, atol=1e-2)
    assert_allclose(bin_edges, [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1],
                    rtol=0, atol=1e-2)


@all_copulas
def test_extra_samples(func, kwargs):
    """Drawing additional samples from a copula does not change the
    realised sequence of the previous samples
    """
    s1 = func(cov, samples=5000, **kwargs)
    s2 = func(cov, samples=9000, **kwargs)
    assert_allclose(s1, s2[:5000], atol=0, rtol=1e-12)


@all_copulas
def test_cov_roundtrip(func, kwargs):
    s = func(cov, samples=65535, **kwargs)
    cov2 = np.corrcoef(s.T)
    assert_allclose(cov, cov2, rtol=0, atol=0.05)


@pytest.mark.parametrize('df,expect_td', [
    (3, [.33, .33, .33]),
    (9, [.20, .20, .20]),
    (999, [.13, .13, .13]),
    ([3, 3, 999, 999], [.33, .08, .13])
])
@pytest.mark.parametrize('rng', ['Mersenne Twister', 'SOBOL'])
@pytest.mark.parametrize('chunks', [None, (65536, 1)])
def test_tail_dependence(df, expect_td, rng, chunks):
    cov2 = [[1.0, 0.5, 0.5, 0.5],
            [0.5, 1.0, 0.5, 0.5],
            [0.5, 0.5, 1.0, 0.5],
            [0.5, 0.5, 0.5, 1.0]]
    s = t_copula(cov2, df=df, samples=262143, rng=rng, chunks=chunks)
    s = scipy.stats.norm.cdf(s)
    actual_td = [
        tail_dependence(s[:, 0], s[:, 1], .99),
        tail_dependence(s[:, 1], s[:, 2], .99),
        tail_dependence(s[:, 2], s[:, 3], .99),
    ]
    assert_allclose(expect_td, actual_td, atol=0.02, rtol=0)
