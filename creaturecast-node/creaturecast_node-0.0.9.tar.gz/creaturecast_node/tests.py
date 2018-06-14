import node
import pprint

class PrintFactory(node.BaseNodeFactory):
    def __init__(self, *args, **kwargs):
        super(PrintFactory, self).__init__(*args, **kwargs)

        self.start_parent.connect(self.print_start_parent)
        self.end_parent.connect(self.print_end_parent)
        self.start_unparent.connect(self.print_start_unparent)
        self.end_unparent.connect(self.print_end_unparent)
        self.root_changed.connect(self.print_root_changed)

    def print_start_parent(self, *args):
        print 'Start Parent ---->', args

    def print_end_parent(self, *args):
        print 'End Parent ---->', args

    def print_start_unparent(self, *args):
        print 'Start UnParent ---->', args

    def print_end_unparent(self, *args):
        print 'End UnParent ---->', args

    def print_root_changed(self, *args):
        print 'Root Changed ---->', args


class RootNode(node.Node):
    def __init__(self, *args, **kwargs):
        kwargs['factory'] = PrintFactory
        super(RootNode, self).__init__(*args, **kwargs)


root = RootNode(name='root')

node = node.Node(parent=root, name='leaf')


pprint.pprint(root.serialize())
