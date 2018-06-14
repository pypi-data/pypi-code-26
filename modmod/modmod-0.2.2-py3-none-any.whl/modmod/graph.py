from collections import defaultdict
import copy
from typing import Tuple

# TODO: clean up references to private members


class Vertex:
  def __init__(self, block_class):
    self._block_class = block_class
    self._block = None
    self._out_edges = []

    self._reset_computation()

  def setup(self, pool):
    self._reset_computation()
    self._block = pool.get(self._block_class)

  def ready(self):
    return all(slot is not None for slot in self._slots)

  def fill_slot(self, idx, value):
    self._slots[idx] = value

  def compute(self):
    return self._block(*tuple(self._slots))

  def add_out_edge(self, edge):
    self._out_edges.append(edge)

  def evaluate(self):
    if self.ready() and not self._computed:
      self._value = self._block(*self._slots)
      self._computed = True
      for edge in self._out_edges:
        edge._tgt.fill_slot(edge._tgt_idx, self._value)
        edge._tgt.evaluate()

  def typecheck(self):
    for edge in self._out_edges:
      (target_type, idx) = edge.input_type_and_idx()
      expected_type = target_type.input_type()[idx]
      if not isinstance(expected_type, Tuple):
        expected_type = (expected_type,)
      if expected_type != self._block_class.output_type():
        return False # TODO: return helpful info about the failure
    return True

  def _reset_computation(self):
    num_slots = len(self._block_class.input_type())
    self._slots = [None,] * num_slots
    self._computed = False
    self._value = None


class Edge:
  def __init__(self, src, tgt, tgt_idx = 0):
    self._src = src
    self._tgt = tgt
    self._tgt_idx = tgt_idx

  def input_type_and_idx(self):
    return (self._tgt._block_class, self._tgt_idx)


class Graph:
  def __init__(self):
    self._pool = None
    self._edges = set()
    self._vertices = set()
    self._input_type = None
    self._entries = []
    self._output_type = None
    self._exit = []

  def inputs(self, input_type, vtx):
    self._input_type = input_type
    self._entries.append(vtx)
    self._vertices.add(vtx)

  def edge(self, src, tgt, tgt_idx=0):
    edge = Edge(src, tgt, tgt_idx)
    self._edges.add(edge)
    self._vertices.add(src)
    self._vertices.add(tgt)
    src.add_out_edge(edge)

  def outputs(self, vtx, output_type):
    self._output_type = output_type
    self._exit.append(vtx)
    self._vertices.add(vtx)

  def dependencies(self):
    return list(set([v._block_class for v in self._vertices]))

  def evaluate(self, pool, args):
    self._pool = pool

    for vtx in self._vertices:
      vtx.setup(self._pool)

    for vtx in self._entries:
      for idx, arg in enumerate(args):
        vtx.fill_slot(idx, arg)
      vtx.evaluate()
    results = list(map(lambda v: v._value, self._exit))
    return results[0] if len(results) == 1 else results

  def typecheck(self):
    for v in self._vertices:
      if not v.typecheck():
        return False # TODO: return helpful info about the failure
    for each in self._entries:
      if each._block_class.input_type() != self._input_type:
        return False
    for each in self._exit:
      if each._block_class.output_type() != self._output_type:
        return False
    return True

