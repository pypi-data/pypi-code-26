import pkg_resources
from functools import partial
from lektor.pluginsystem import Plugin
from lektor.context import get_ctx
from lektor.assets import get_asset
import os.path

from pybtex.database.input import bibtex as pybibtex
import pybtex.style.names.plain as myplain

plain = myplain.NameStyle().format

def generic_filter(x, key, searchterm):
    try:
        if x[1].fields[key].lower().find(searchterm) >= 0:
            return True
        else:
            return False
    except:
        return False


def filterbibtex(bib, name=None, year=None, tag=None, labels=None, fname=None):

    if not fname:
        fname = bib.keys()

    if not labels:
        labels = []  # gather all labels
        for f in fname:
            allrefs = set(label[0] for label in bib[f].entries.items())
            if name:
                myfilter = partial(generic_filter, key='author', searchterm=name)
                bib1 = set(label[0] for label in filter(myfilter, bib[f].entries.items()))
                allrefs = allrefs.intersection(bib1)
            if tag:
                myfilter = partial(generic_filter, key='tags', searchterm=tag)
                bib2 = set(label[0] for label in filter(myfilter, bib[f].entries.items()))
                allrefs = allrefs.intersection(bib2)
            if year:
                myfilter = partial(generic_filter, key='year', searchterm=year)
                bib3 = set(label[0] for label in filter(myfilter, bib[f].entries.items()))
                allrefs = allrefs.intersection(bib3)
            labels += list(allrefs)

    if type(labels) == str:
        labels = [labels]

    bibout = []
    for label in labels:
        found = False
        for f in bib.keys():
            entry = bib[f].entries.get(label)
            if entry:
                bibout.append([label, entry])
                found = True
        if not found:
            print("bibtex warning: can't use entry", label)

    return bibout


def parse_bibtex(bib, template, env):
    # change datastructure to list and add bibkey as a normal field
    newlist = []
    for b in bib:
        key, value = b
        X = value.fields
        X['bibkey'] = key
        # what type of publication
        X['type'] = value.type
        # pretty print the names and also keep a bibtexcopy for bibtex output
        for k, v in value.persons.items():
            X[k] = ' and '.join(plain(item).format().render_as('html') for item in v)

        tmp = X.get('author', '')
        # we want the author list formated nicely and not all the bibtex 'and's in there
        X['newauthor'] = ', '.join(x.strip() for x in tmp.split(' and', tmp.count('and')-1))

        tmp = X.get('editor', '')
        X['neweditor'] = ', '.join(x.strip() for x in tmp.split(' and', tmp.count('and')-1))
        # also remove all {} from the output and replace umlaute and other special characters
        myreplace = {'{': '', '}': '', '\\&': '&', '\\"a': '&auml;', '\\"A': '&Auml;',
                     '\\"u': '&uuml;', '\\"U': '&Uuml;', '\\"o': '&ouml;', '\\"O': '&Ouml;'}
        for a, b in X.items():
            if isinstance(b, str) or isinstance(b, unicode):
                for i, j in myreplace.items():
                    X[a] = X[a].replace(i, j)
        # save entry
        newlist.append(X)

    parsed = env.render_template(template, this=newlist)
    return parsed

class BibtexSupportPlugin(Plugin):
    name = 'Bibtex-support'
    description = """Bibtex file support to include publication list. Multiple bibtex
files and filtering by name, year, tag, and label are supported."""


    def __init__(self, env, id):
        super().__init__(env, id)

        config = self.get_config()
        self.bibfiles = config.get('Bibtex.files', []).strip().split()
        self.template = config.get('Bibtex.template', 'lektor_bibtex_support_default_template.html')

        pkg_dir = pkg_resources.resource_filename('lektor_bibtex_support', 'templates')
        r = self.env.jinja_env.loader.searchpath.append(pkg_dir)
        self.bib_data = {}
        for f in self.bibfiles:
            # need separate parsers for each file, otherwise they get added together
            parser = pybibtex.Parser()
            self.bib_data[f] = parser.parse_file(os.path.join(env.root_path, 'assets',f))

    def list_publications(self, name=None, tag=None, year=None, labels=None, fname=None):
        bib = filterbibtex(self.bib_data, name=name, tag=tag, year=year, labels=labels, fname=fname)
        return parse_bibtex(bib, self.template, self.env)


    def on_setup_env(self, **extra):
        self.env.jinja_env.globals.update(
            list_publications=self.list_publications
        )
