import itertools
import collections
import imp
import os
import creaturecast_rigging.math as mth
import creaturecast_node.node as nod
import re



def get_classes(module):
    md = module.__dict__
    return [
        md[c] for c in md if (
            isinstance(md[c], type) and md[c].__module__ == module.__name__
        )
    ]


def get_package_contents(package_name):
    file, pathname, description = imp.find_module(package_name)
    if file:
        raise ImportError('Not a package: %r', package_name)
    # Use a set because some may be both source and compiled.
    return set([os.path.splitext(module)[0]
                for module in os.listdir(pathname)
                if module.endswith('.py')])


def create_alpha_dictionary(depth=4):
    ad = {}
    mit = 0
    for its in range(depth)[1:]:
        for combo in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=its):
            ad[mit] = ''.join(combo)
            mit += 1
    return ad

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def force_iterable(obj):
    if not isinstance(obj, collections.Iterable) or isinstance(obj, basestring):
        obj = [obj]
    return obj

alpha_dictionary = create_alpha_dictionary()



def list_poly_transforms(namespace=None):
    transforms = []
    if namespace:
        mesh_nodes = mya.cmds.ls('%s:*' % namespace, type='mesh', l=True)
    else:
        mesh_nodes = mya.cmds.ls(type='mesh', l=True)
    for mesh in mesh_nodes:
        parent = mya.cmds.listRelatives(mesh, p=1, f=False)[0]
        if parent not in transforms:
            attr_node = parent
            transforms.append(attr_node)
    return transforms


def get_edge_loops(target, initial_edge_numbers=0):
    mya.cmds.select(target)
    edge_loops = []
    for edge in mya.cmds.polySelect(edgeRing=initial_edge_numbers, q=1):
        mya.cmds.polySelect(edgeLoop=edge)
        edge_loops.append(mya.cmds.ls(sl=1))
    return edge_loops


def get_vertex_normal(vert):
    normals = mya.cmds.polyNormalPerVertex(vert, q=True, xyz=True)
    chunks = [c for c in cut.chunks(normals, 3)]

    x, y, z = (0.0, 0.0, 0.0)

    for c in chunks:
        x += c[0]
        y += c[1]
        z += c[2]

    vector = [x/len(chunks), y/len(chunks), z/len(chunks)]
    return vector


def build_matrix_from_verts(vert1, vert2):
    p1 = mya.cmds.xform(vert1, q=True, ws=True, t=True)
    p2 = mya.cmds.xform(vert2, q=True, ws=True, t=True)
    return mtx.triangulate_matrix(p1, p2, get_vertex_normal(vert1))


def camelcase_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def underscore_to_camelcase(value):
    def camelcase():
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))


def create_symmetry_data(count, side, size):

    data = dict(indices=range(count), sides=[side]*count, positions=[])

    if side == 2:
        if mth.iseven(count):
            data['indices'] = range(count / 2)[::-1]
            data['indices'].extend(range(count / 2))
            data['sides'] = [1] * (count / 2)
            data['sides'].extend([-1] * (count / 2))
        else:
            data['indices'] = range((count-1)/2)[::-1]
            data['indices'].append(0)
            data['indices'].extend(range((count-1)/2))
            data['sides'] = [1] * ((count-1)/2)
            data['sides'].append(0)
            data['sides'].extend([-1] * ((count-1)/2))

    for itr in range(count):
        side = data['sides'][itr]
        if mth.iseven(count):
            b = 1.5
        else:
            b = 3.0
        bump_value = (b*size*float(data['sides'][itr]))
        if side == 0:
            data['positions'].append([0.0, 3.0*(size*float(itr)), 0.0])
        else:
            data['positions'].append([3.0*float(data['indices'][itr])
                * float(size)
                * float(data['sides'][itr])
                + bump_value, 0.0, 0.0])
        if side == 2:
            for i in range(len(data['positions'])):
                data['positions'][i][1] = 0

    return data


def kill_namespaces():
    curNS = mya.cmds.namespaceInfo( lon=True )
    defaults = ["UI", "shared", "camera01"]
    diff = [item for item in curNS if item not in defaults]

    for ns in diff:
        if mya.cmds.namespace( exists=str(ns)):
            mya.cmds.namespace(rm=str(ns))



def get_side_aim_vector(side):
    if side == -1:
        return [x * -1 for x in nod.rig_settings['aim_vector']]
    return nod.rig_settings['aim_vector']


def get_side_up_vector(side):
    if side == -1:
        return [x * -1 for x in nod.rig_settings['up_vector']]
    return nod.rig_settings['up_vector']
