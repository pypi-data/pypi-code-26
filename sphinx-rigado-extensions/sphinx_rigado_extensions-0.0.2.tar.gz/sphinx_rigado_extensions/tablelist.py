# -*- coding: utf-8 -*-
"""
    An extension that adds tablelist and figurelist directives
    that will populate with lists of the tables and figures
    contained in the current document.

    Only works with html builders

    Usage:

    .. tablelist::

    .. figurelist::
"""

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util.nodes import clean_astext
from docutils.nodes import fully_normalize_name

def setup(app):
    app.add_node(tablelist,
                 html=(visit_pass, depart_pass))
    app.add_node(figurelist,
                 html=(visit_pass, depart_pass))
    app.add_directive('tablelist', TablelistDirective)
    app.add_directive('figurelist', FigurelistDirective)
    app.connect('doctree-resolved', process_tablelists)
    app.connect('doctree-resolved', process_figurelists)

    return {'version': '0.1'}

def visit_pass(self, node):
    pass
def depart_pass(self, node):
    pass

class tablelist(nodes.General, nodes.Element):
    pass
class figurelist(nodes.General, nodes.Element):
    pass

class TablelistDirective(Directive):
    def run(self):
        return [tablelist('')]

class FigurelistDirective(Directive):
    def run(self):
        return [figurelist('')]

def process_tablelists(app, doctree, fromdocname):
    process_lists(app, doctree, fromdocname, tablelist, nodes.table)

def process_figurelists(app, doctree, fromdocname):
    process_lists(app, doctree, fromdocname, figurelist, nodes.figure)

def ancestorOfClass(node, ancestorclassname):
    if node.__class__.__name__ == ancestorclassname:
        return node
    elif hasattr(node, 'parent'):
        return ancestorOfClass(node.parent, ancestorclassname)
    else:
        return False

def process_lists(app, doctree, fromdocname, list_directive, target_directive):
    ns = dict((k, app.config[k]) for k in app.config.values)
    ns.update(app.config.__dict__.copy())
    ns['builder'] = app.builder.name

    # Replace all figurelist nodes with a list of the collected figures.
    # Augment each figure name with a backlink to the original location.
    for node in doctree.traverse(list_directive):

        # lists of figures and tables in latex are handled elsewhere
        if app.builder.name == 'latex':
            node.replace_self(nodes.Text(''))
            continue

        content = ""
        for subnode in doctree.traverse(target_directive):
            # make sure subnode isn't in an ifconfig block that would remove it from output
            ifconfigAncestor = ancestorOfClass(subnode, 'ifconfig')
            ifconfigOK = True

            if ifconfigAncestor:
                try:
                    ifconfigOK = eval(ifconfigAncestor['expr'], ns)
                except Exception as err:
                    pass
            if ifconfigOK:
                made = makecontent(subnode, fromdocname, app.builder.env)
                if app.builder.name == 'html':
                    content += made['html']
                else:
                    content += made['text']

        if app.builder.name == 'html':
            content = '<p>%s</p>' % (content)
            node.replace_self(nodes.raw(content, content, format='html'))
        else:
            node.replace_self(nodes.Text(content))

def makecontent(node, docname, env):
    figname = get_fig_title(node)
    figtype = get_fig_type(node)
    try:
        figid = node['ids'][0]
        fignumber = env.toc_fignumbers[docname][figtype][figid]
    except (KeyError, IndexError):
        # target_node is found, but fignumber is not assigned.
        # Maybe it is defined in orphaned document.
        env.warn(docname, "no number is assigned for %s: %s" % (figtype, figname), lineno=node.line)
        return {'html': '', 'text': ''}

    title = env.config.numfig_format.get(figtype, '')

    try:
        newtitle = title % '.'.join(map(str, fignumber))
    except TypeError:
        env.warn(fromdocname, 'invalid numfig_format: %s' % title,
                 lineno=node.line)
        return {'html': '', 'text': ''}

    html = '<a href="#%s">%s%s</a><br />' % (figid, newtitle, figname)
    text = '%s%s\n' % (newtitle, figname)
    return {'html': html, 'text': text}

def get_fig_title(node):
    for subnode in node:
        if subnode.tagname in ('caption', 'title'):
            return clean_astext(subnode)
    return ""

enumerable_nodes = {
    nodes.table: 'table',
    nodes.figure: 'figure',
    nodes.container: 'code-block'
}

def get_fig_type(node):

    def has_child(node, cls):
        return any(isinstance(child, cls) for child in node)

    if isinstance(node, nodes.container):
        if node.get('literal_block') and has_child(node, nodes.literal_block):
            return 'code-block'
        else:
            return None
    else:
        figtype = enumerable_nodes.get(node.__class__, None)
        return figtype
