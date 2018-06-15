import tensorflow as tf

def coords_to_image_tf(coords, a, L):
    """
    Prepares the ops necessary to take a list of atom coordinates and
    produce dim-dimensional images of dimension dim of Gaussians
    centred on the atoms.

    Args:
        coords:  TensorFlow placeholder of size [None, dim] or [N, dim],
            where axis 0 represents atoms and axis 1 dimensions (e.g. x,y,z).
            e.g. a [500, 2] coords placeholder would represent 500 x,y pairs
        a (list of float32): Lattice constants for each of the dim dimensions
        L (list of int): Number of pixels in the output image in each dimension

    Returns:
        image: Tensor of shape L representing the output image.

    """

#    assert coords.shape[1] <= 3, "More than three-dimensional images are not supported. coords shape={}".format(coords.shape)
#    assert coords.shape[1]==len(a), "Placeholder coords must have same second dimenson as a has first"
    assert len(a) == len(L), "a and L must be the same length, probably 2 or 3 (2d or 3d)"


    dim = len(a)
    dx = [a[i] / L[i] for i in range(dim)]

    mesh = tf.meshgrid(*[tf.range(L[i]) for i in range(dim)])
    assert len(mesh)==dim, "Something's wrong. len(mesh)={}, dim={}".format(len(mesh), dim)
    mesh = [tf.cast(mesh[i], tf.float32)*dx[i] for i in range(dim)]

    if dim==1:
        image = tf.cond(tf.shape(coords)[0] > 0,
                        true_fn=lambda: tf.reduce_sum(tf.map_fn(lambda coord: coord[0] * tf.exp(-((mesh[0]-coord[1])**2) / (2 * (0.2**2))),
                                                      coords,parallel_iterations=256,),axis=0), 
                        false_fn=lambda: tf.zeros(L)
                       )
    elif dim==2:
        image = tf.cond(tf.shape(coords)[0] > 0,
                        true_fn=lambda: tf.reduce_sum(tf.map_fn(lambda coord: coord[0] * tf.exp(-((mesh[0]-coord[1])**2 + (mesh[1]-coord[2])**2) / (2 * (0.2**2))),coords,parallel_iterations=256,),axis=0),
                        false_fn=lambda: tf.zeros(L)
                        )
    elif dim==3:
        image = tf.cond(tf.shape(coords)[0] > 0,
                                true_fn=lambda: tf.reduce_sum(tf.map_fn(lambda coord: coord[0] * tf.exp(-((mesh[0]-coord[1])**2 + (mesh[1]-coord[2])**2 + (mesh[2]-coord[3])**2) / (2 * (0.2**2))),
                                    coords,parallel_iterations=256,),axis=0),
                                false_fn=lambda: tf.zeros(L)
                                )


    return image





def coords_to_image_tf_COMPAT(coords, a, L):
    """
    Compatible with tensorflow<=1.1 (uses deprecated fn1 and fn2 calls to tf.cond)
    Prepares the ops necessary to take a list of atom coordinates and
    produce dim-dimensional images of dimension dim of Gaussians
    centred on the atoms.

    Args:
        coords:  TensorFlow placeholder of size [None, dim] or [N, dim],
            where axis 0 represents atoms and axis 1 dimensions (e.g. x,y,z).
            e.g. a [500, 2] coords placeholder would represent 500 x,y pairs
        a (list of float32): Lattice constants for each of the dim dimensions
        L (list of int): Number of pixels in the output image in each dimension

    Returns:
        image: Tensor of shape L representing the output image.

    """

#    assert coords.shape[1] <= 3, "More than three-dimensional images are not supported. coords shape={}".format(coords.shape)
#    assert coords.shape[1]==len(a), "Placeholder coords must have same second dimenson as a has first"
    assert len(a) == len(L), "a and L must be the same length, probably 2 or 3 (2d or 3d)"


    dim = len(a)
    dx = [a[i] / L[i] for i in range(dim)]

    mesh = tf.meshgrid(*[tf.range(L[i]) for i in range(dim)])
    assert len(mesh)==dim, "Something's wrong. len(mesh)={}, dim={}".format(len(mesh), dim)
    mesh = [tf.cast(mesh[i], tf.float32)*dx[i] for i in range(dim)]

    if dim==1:
        image = tf.cond(tf.shape(coords)[0] > 0,
                        fn1=lambda: tf.reduce_sum(tf.map_fn(lambda coord: coord[0] * tf.exp(-((mesh[0]-coord[1])**2) / (2 * (0.2**2))),
                                                      coords,parallel_iterations=256,),axis=0), 
                        fn2=lambda: tf.zeros(L)
                       )
    elif dim==2:
        image = tf.cond(tf.shape(coords)[0] > 0,
                        fn1=lambda: tf.reduce_sum(tf.map_fn(lambda coord: coord[0] * tf.exp(-((mesh[0]-coord[1])**2 + (mesh[1]-coord[2])**2) / (2 * (0.2**2))),coords,parallel_iterations=256,),axis=0),
                        fn2=lambda: tf.zeros(L)
                        )
    elif dim==3:
        image = tf.cond(tf.shape(coords)[0] > 0,
                                fn1=lambda: tf.reduce_sum(tf.map_fn(lambda coord: coord[0] * tf.exp(-((mesh[0]-coord[1])**2 + (mesh[1]-coord[2])**2 + (mesh[2]-coord[3])**2) / (2 * (0.2**2))),
                                    coords,parallel_iterations=256,),axis=0),
                                fn2=lambda: tf.zeros(L)
                                )


    return image

