import pkg_resources
import numpy
numpy.random.seed(10)
import os


def test_cnn8():
    """ test for the CNN8 architecture

        this architecture takes 3x128x128 images as input
        output an embedding of dimension 512
    """
    from . import CNN8Extractor
    extractor = CNN8Extractor()
    data = numpy.random.rand(3, 128, 128).astype("float32")
    output = extractor(data)
    assert output.shape[0] == 512

def test_casianet():
    """ test for the CasiaNet architecture

        this architecture takes 3x128x128 images as input
        output an embedding of dimension 320
    """
    from . import CasiaNetExtractor
    extractor = CasiaNetExtractor()
    # this architecture expects 3x128x128 images
    data = numpy.random.rand(3, 128, 128).astype("float32")
    output = extractor(data)
    assert output.shape[0] == 320
