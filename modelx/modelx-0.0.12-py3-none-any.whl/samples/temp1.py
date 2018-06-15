import modelx as mx

m, space = mx.new_model(), mx.new_space()

@mx.defcells
def f0():
    return 3

@mx.defcells
def f2(x, y=1):
    return x + y

@mx.defcells
def f1(x):
    return 2 * x

# space.to_frame()

# f0, f1, f2 = mx.defcells(f0, f1, f2)




# df = space.to_frame(())

df1 = space.cells['f1', 'f2'].to_frame((1, 2), (3, 4), (5, 6))

# df2 = space.to_frame(1, 2, 3)


# space.frame.index.names == ['x', 'y']





