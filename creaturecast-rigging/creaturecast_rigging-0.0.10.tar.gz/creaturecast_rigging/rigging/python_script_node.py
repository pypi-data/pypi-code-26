import creaturecast_node.node as nod


class PythonScriptNode(nod.Node):

    default_data = dict(
        icon='python_grey',
        root_name='script',
        siffix='psn',
        created=False,
        layer='script',
        code=''
    )

    def __init__(self, *args, **kwargs):
        super(PythonScriptNode, self).__init__(*args, **kwargs)
