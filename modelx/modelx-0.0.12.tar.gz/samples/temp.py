import modelx as mx
from modelx.core.cells import CellArgs

simplemodel = mx.new_model()

space = simplemodel.new_space()

@mx.defcells
def fibo(x):
    if x == 0 or x == 1:
        return x
    else:
        return fibo(x - 1) + fibo(x - 2)

def get_predec(node):
    return simplemodel._impl.cellgraph.predecessors(node)

def get_succ(node):
    return simplemodel._impl.cellgraph.successors(node)

space.fibo[10]

for x in range(10):
    fibo = CellArgs(space.fibo._impl, x)
    fibo_prev1 = CellArgs(space.fibo._impl, x - 1)
    fibo_prev2 = CellArgs(space.fibo._impl, x - 2)
    fibo_next1 = CellArgs(space.fibo._impl, x + 1)
    fibo_next2 = CellArgs(space.fibo._impl, x + 2)

    predec = simplemodel._impl.cellgraph.predecessors(fibo)
    succ = simplemodel._impl.cellgraph.successors(fibo)

    if x == 0 or x == 1:
        assert list(get_predec(fibo)) == []
        assert fibo_next2 in get_succ(fibo)
    elif x < 9:
        assert fibo_prev1 in get_predec(fibo)
        assert fibo_prev2 in get_predec(fibo)
        assert fibo_next1 in get_succ(fibo)
        assert fibo_next2 in get_succ(fibo)