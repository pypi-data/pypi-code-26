from abc import ABC, abstractmethod
import modmod.graph
import modmod.block
from modmod.pool import DEFAULT_POOL_NAME


class Model(ABC):
  def __init__(self, deps, pool, config):
    self._deps = deps
    self._pool = pool
    self._config = config

  @staticmethod
  @abstractmethod
  def input_type():
    pass

  @staticmethod
  @abstractmethod
  def output_type():
    pass

  @staticmethod
  @abstractmethod
  def _generate_graph():
    pass

  @classmethod
  def create(cls, pool, config):
    dep_classes = cls._dependencies(pool)
    deps = []

    for dep in dep_classes:
      deps.append(pool.get(dep))

    return cls(deps, pool, config)

  @classmethod
  def get(cls, poolname=DEFAULT_POOL_NAME):
    """Fetches an instance of this model from the shared pool.

    :param  poolname: which pool to fetch from (defaults to global)
    """
    pool = modmod.pool.get(poolname)
    return pool.get(cls)

  @classmethod
  def _dependencies(cls, pool):
    graph = cls._generate_graph()
    return list(graph.dependencies())

  @staticmethod
  def __create_dependency(dep, pool, config):
    if issubclass(dep, modmod.model.Model):
      model = dep.create(pool, config)
      pool._add_block(model, dep)
    elif issubclass(dep, modmod.block.Block):
      for subdep in dep._dependencies():
        Model.__create_dependency(subdep, pool, config)
      block = dep.create(pool, config)
      pool._add_block(block, dep)

  def __call__(self, *args):
    graph = self._generate_graph()
    return graph.evaluate(self._pool, args)


  @classmethod
  def typecheck(cls):
    graph = cls._generate_graph()
    return graph.typecheck()

