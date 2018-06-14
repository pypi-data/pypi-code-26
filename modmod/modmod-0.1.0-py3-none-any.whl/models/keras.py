from abc import abstractmethod
import datetime
import math
from modmod.model import Model
from modmod.blocks.keras import KerasBlock


class KerasModel(Model):
  def setup_training(self, optimizer, block_cls=None):
    """Finds and sets up a trainable KerasBlock with the supplied optimizer."""
    trainable_block = self._find_trainable_block(block_cls)
    trainable_block.setup_training(optimizer)

  def train(self, inputs, outputs, pool, base_filename, save_model=True, save_weights=True,epochs=1, save_every=1, block_cls=None, **kwargs):
    """Finds and trains a trainable KerasBlock."""
    trainable_block = self._find_trainable_block(block_cls)
    block_cls = trainable_block.__class__
    training_graph = self._generate_training_graph(block_cls)
    prepped_inputs = [training_graph.evaluate(pool, x) for x in inputs]

    date = datetime.datetime.now().strftime('%Y-%m-%d')
    cycles = math.ceil(epochs / save_every)

    for cycle_num in range(0, cycles):
      trainable_block.train(prepped_inputs, outputs, epochs=save_every, **kwargs)
      save_filename = '{base}_{date}_c{cycle}'.format(base=base_filename, date=date, cycle=cycle_num)
      trainable_block.save(save_filename, model=save_model, weights=save_weights)


  def save(self, base_filename, block_cls=None, model=True, weights=True):
    """Finds and saves a KerasBlock's weights and/or model at the specified location."""
    trainable_block = self._find_trainable_block(block_cls)
    trainable_block.save(base_filename, model=model, weights=weights)

  def _find_trainable_block(self, block_cls=None):
    # TODO: raise a helpful error if no trainable blocks were found
    if block_cls == None:
      return next(filter(lambda d: isinstance(d, KerasBlock), self._deps))
    else:
      return next(filter(lambda d: isinstance(d, block_cls), self._deps))

  @abstractmethod
  def _generate_training_graph(block_cls):
    """Return a training graph for the specified trainable block."""
    pass

