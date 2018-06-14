from abc import ABC, abstractmethod
import modmod.pool
from modmod.pool import DEFAULT_POOL_NAME


class Block(ABC):

  @staticmethod
  @abstractmethod
  def input_type():
    """Specifies the input type that this block requires.

    For example, a tokenizer may have an input type (str,).

    :return:  a tuple containing the type(s) of the input arguments.
    """
    pass

  @staticmethod
  @abstractmethod
  def output_type():
    """Specifies the input type that this block requires.

    For example, a tokenizer may have an output type (typing.List[str],).

    :return:  a tuple containing the type(s) of the outputs.
    """
    pass

  @staticmethod
  @abstractmethod
  def create(pool, config):
    """Creates an instance of this block.

    :param  config: the options for this environment (data location, etc.)
    :return:  an instance of this Block
    """
    pass

  @abstractmethod
  def __call__(self, *args):
    pass

  @staticmethod
  def _dependencies():
    return []

  @classmethod
  def get(cls, poolname=DEFAULT_POOL_NAME):
    """Fetches an instance of this block from the shared pool.

    :param  poolname: which pool to fetch from (defaults to global)
    """
    pool = modmod.pool.get(poolname)
    return pool.get(cls)


def create_block(input_type, output_type, call, init = None,
    dependencies = [], name = None):
  """Helper function to make creating new block types easier.

    This is primarily to assist in testing and for creating small blocks. For
    any reasonably complex blocks, it makes more sense to explicitly define the
    class.

    :param  input_type:   the type this block expects
    :param  output_type:  the type this block returns
    :param  call:         a function which accepts args and state and returns the result
    :param  init:         an initializer for stored (typically read-only) state
    :param  dependencies: a list of the dependencies for this block.
    :param  name:         the name of the class we are creating
  """
  class AnonymousBlock(Block):
    if init:
      def __init__(self, state):
        self._state = state

    @staticmethod
    def input_type():
      return input_type

    @staticmethod
    def output_type():
      return output_type

    if init:
      @staticmethod
      def create(pool, config):
        state = init()
        return AnonymousBlock(state)
    else:
      @staticmethod
      def create(pool, config):
        return AnonymousBlock()

    if init:
      def __call__(self, *args):
        return call(self._state, *args)
    else:
      def __call__(self, *args):
        return call(*args)

    @staticmethod
    def _dependencies():
      return dependencies
  if name is not None:
    return type(name, (AnonymousBlock,), {})
  else:
    return AnonymousBlock
