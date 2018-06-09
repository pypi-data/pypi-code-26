import logging.config
from functools import reduce


__all__ = 'configure', 'resolve'


class Configurator(logging.config.BaseConfigurator):

  auto_factory = None
  '''Flag that controls auto-invocation of "()" factories'''

  config = None
  '''``ConvertingDict`` instance'''


  def __init__(self, config, auto_factory = True):
    self.auto_factory = auto_factory
    self.config = self.create_dict(config)

  def create_dict(self, config):
    d = ConvertingDict(config)
    d.configurator = self
    d.convert_items()
    return d

  def convert(self, value):
    if isinstance(value, dict):
      if not isinstance(value, ConvertingDict):
        value = self.create_dict(value)
      if self.auto_factory and '()' in value:
        value = self.configure_custom(value)

    return super(Configurator, self).convert(value)


class ConvertingDict(dict, logging.config.ConvertingMixin):

  def convert_items(self):
    for k, v in self.items():
      self.convert_with_key(k, v)


def merge(target, source):
  '''Deep ``dict`` merge'''

  result = target.copy()  # shallow copy
  stack  = [(result, source)]
  while stack:
    currentTarget, currentSource = stack.pop()
    for key in currentSource:
      if key not in currentTarget:
        currentTarget[key] = currentSource[key]  # appending
      else:
        if isinstance(currentTarget[key], dict) and isinstance(currentSource[key], dict):
          currentTarget[key] = currentTarget[key].copy()  # nested dict copy
          stack.append((currentTarget[key], currentSource[key]))
        elif currentTarget[key] is not None and currentSource[key] is None:
          del currentTarget[key]  # remove key marked as None
        else:
          currentTarget[key] = currentSource[key]  # overriding

  return result


def configure(*args, **kwargs):
  '''Merged nested configuration dictionary is wrapped into a resolver'''

  merged = reduce(merge, args)
  return Configurator(merged, **kwargs).config


resolve = logging.config._resolve

