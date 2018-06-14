

class Pool:

  def __init__(self, config = {}):
    self._blocks = {}
    self._config = config

  def get(self, block_class):
    if block_class not in self._blocks:
      self._create_block(block_class)
    return self._blocks[block_class]

  def _add_block(self, block, cls):
    self._blocks[cls] = block

  def _create_block(self, block_class):
    block = block_class.create(self, self._config)
    self._add_block(block, block_class)

  def __contains__(self, block_class):
    return block_class in self._blocks


DEFAULT_POOL_NAME = 'global'


shared_pools = {
    DEFAULT_POOL_NAME: Pool()
}


def configure(config, name=DEFAULT_POOL_NAME):
  """Sets the configuration for the global pool.

  NOTE: if the global pool has been used, this is a *destructive* operation
  and will create an entirely new pool. This is necessary to ensure that all
  objects created from the pool will be consistent with the new config.

  :param  config: a dictionary containing the configuration parameters
  :param  name:   which pool to configure (defaults to the global pool)
  """
  global shared_pools
  pool = Pool(config)
  shared_pools[name] = pool


def get(name=DEFAULT_POOL_NAME):
  """Gets a pool with the specified name, or the global pool."""
  global shared_pools
  return shared_pools[name]

