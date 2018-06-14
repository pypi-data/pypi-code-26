
import creaturecast_rigging.nodes.depend_node as dep


def create_skin_cluster(*args, **kwargs):


    args = flatten_nodes(*args)

    if len(args) < 2:
        raise Exception('Need at least two nodes to create a skin cluster')
    if 'parent' not in kwargs:
        kwargs['parent'] = args[-1]
    skin_cluster = SkinCluster(parent=args[-1])
    skin_cluster.nodes['influences'] = args[0:-1]
    skin_cluster.nodes['geometry'] = args[-1]
    return skin_cluster


class SkinCluster(dep.DependNode):

    default_data = dict(
        icon='skull_button_white',
        suffix='skn',
        layer='deformer',
        base_type='skin_cluster',
        node_type='skinCluster'
    )

    def __init__(self, *args, **kwargs):
        super(SkinCluster, self).__init__(*args, **kwargs)


def flatten_nodes(*args):
    flattened_args = []
    for arg in args:
        if isinstance(arg, (list, tuple, set)):
            flattened_args.extend(flatten_nodes(*[x for x in arg]))
        elif isinstance(arg, dict):
            flattened_args.extend(flatten_nodes(*arg.values()))
        else:
            flattened_args.append(arg)
    return flattened_args
