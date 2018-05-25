import numpy

import torch
from torch.autograd import Variable

import torchvision.transforms as transforms

from bob.learn.pytorch.architectures import CNN8
from bob.bio.base.extractor import Extractor

class CNN8Extractor(Extractor):
  """ The class implementing the feature extraction of CASIA-Net embeddings.

  Attributes
  ----------
  network: :py:class:`torch.nn.Module`
      The network architecture
  to_tensor: :py:mod:`torchvision.transforms`
      The transform from numpy.array to torch.Tensor
  norm: :py:mod:`torchvision.transforms`
      The transform to normalize the input 

  """
  
  def __init__(self, model_file=None, num_classes=10575):
    """ Init method

    Parameters
    ----------
    model_file: str
        The path of the trained network to load
    drop_rate: float
        The number of classes.
    
    """

    Extractor.__init__(self, skip_extractor_training=True)
    
    # model
    self.network = CNN8(num_classes)
    if model_file is None:
      # do nothing (used mainly for unit testing) 
      pass
    else:
      cp = torch.load(model_file)
      if 'state_dict' in cp:
        self.network.load_state_dict(cp['state_dict'])
    self.network.eval()

    # image pre-processing
    self.to_tensor = transforms.ToTensor()
    self.norm = transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))

  def __call__(self, image):
    """ Extract features from an image

    Parameters
    ----------
    image : 3D :py:class:`numpy.ndarray` (floats)
      The image to extract the features from. Its size must be 3x128x128

    Returns
    -------
    feature : 2D :py:class:`numpy.ndarray` (floats)
      The extracted features as a 1d array of size 320 
    
    """
   
    input_image = numpy.rollaxis(numpy.rollaxis(image, 2),2)
    input_image = self.to_tensor(input_image)
    input_image = self.norm(input_image)
    input_image = input_image.unsqueeze(0)
    _, features = self.network.forward(Variable(input_image))
    features = features.data.numpy().flatten()

    # normalize
    std = numpy.sqrt((features ** 2).sum(-1))
    features /= (std+1e-10)

    return features
