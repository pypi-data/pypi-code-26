from nose.tools import raises
import cynetworkx as nx

# smoke tests for exceptions


@raises(nx.NetworkXException)
def test_raises_cynetworkxexception():
    raise nx.NetworkXException


@raises(nx.NetworkXError)
def test_raises_cynetworkxerr():
    raise nx.NetworkXError


@raises(nx.NetworkXPointlessConcept)
def test_raises_cynetworkx_pointless_concept():
    raise nx.NetworkXPointlessConcept


@raises(nx.NetworkXAlgorithmError)
def test_raises_cynetworkxalgorithmerr():
    raise nx.NetworkXAlgorithmError


@raises(nx.NetworkXUnfeasible)
def test_raises_cynetworkx_unfeasible():
    raise nx.NetworkXUnfeasible


@raises(nx.NetworkXNoPath)
def test_raises_cynetworkx_no_path():
    raise nx.NetworkXNoPath


@raises(nx.NetworkXUnbounded)
def test_raises_cynetworkx_unbounded():
    raise nx.NetworkXUnbounded
