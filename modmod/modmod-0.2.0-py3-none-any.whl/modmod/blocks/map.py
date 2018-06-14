import modmod.block
import modmod.model
from typing import List


def Map(wrapped_type):
  if issubclass(wrapped_type, modmod.block.Block):
    class MappedBlock(modmod.block.Block):
      def __init__(self, inner):
        self._inner = inner

      @staticmethod
      def input_type():
        return (List[wrapped_type.input_type()],)

      @staticmethod
      def output_type():
        return (List[wrapped_type.output_type()],)

      @staticmethod
      def create(pool, config):
        inner = pool.get(wrapped_type)
        return MappedBlock(inner)

      def __call__(self, args):
        f = self._inner
        return [f(x) for x in args]

    return MappedBlock
  else:
    pass # TODO: allow wrapping models


