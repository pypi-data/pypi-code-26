from abc import ABC, abstractmethod
from modmod.block import Block


class KerasBlock(Block):
  @abstractmethod
  def setup_training(self, optimizer):
    """Compile the model with the supplied optimizer.

      :param  optimizer:  the optimizer to use for training this model
      :return:  None
    """
    pass

  @abstractmethod
  def train(self, inputs, outputs, epochs=1, **kwargs):
    """Trains the model on the supplied data.

      :param  inputs:   the inputs to train on
      :param  outputs:  the expected output
      :param  epochs:   how many epochs to train for
      :param  kwargs:   a dictionary of other arguments to fit the model (i.e. num epochs)
      :return:  None
    """
    pass

  @abstractmethod
  def save(self, base_filename, model=True, weights=True):
    """Saves the model and/or weights.

      :param  base_filename:  the location and partial filename where you want to save the model
      :param  model:          save the model? True/False
      :param  weights:        save the weights? True/False
      :return:  None
    """
