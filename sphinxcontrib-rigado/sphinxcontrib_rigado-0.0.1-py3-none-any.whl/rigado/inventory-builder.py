from sphinx.builders.html import StandaloneHTMLBuilder

class InventoryBuilder(StandaloneHTMLBuilder):
    name = 'inventory'

    def write_doc(self, docname, doctree):
        pass

    def finish(self):
        self.dump_inventory()


def setup(app):
    app.add_builder(InventoryBuilder)
