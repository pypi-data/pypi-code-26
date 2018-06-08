from copy import deepcopy
from textwrap import TextWrapper
import yaml
from .utils import file_write



# Metadata entries are tupels with the form:
# (entry_name, documentation, value)
# These constants can be used to acces them more obviously:
NAME = 0
DOC = 1
VALUE = 2


doc_wrap = TextWrapper(width=78, initial_indent="# ", subsequent_indent="# ").wrap


class Metadata(object):
    '''
    Create a new metadata instance. Accepts a dictionary with the blocknames
    as keys and a list with the entries as the value.
    '''
    def __init__(self, metadata=None):
        self.metadata = metadata or {}
        if metadata:
            for key, val in metadata.items():
                self.add_block(key, *val)

    def add_block(self, block_name, *entries):
        '''Add a new block to the metadata. Accepts entries to be added to the new block.'''
        self.metadata[block_name] = {entry[NAME]: entry for entry in entries}

    def add_to_block(self, block_name, *entries):
        '''Add entrie to an existing block'''
        for entry in entries:
            self.metadata[block_name][entry[NAME]] = entry

    def replace(self, *entries):
        '''Replace an existing entry with a new one with the same name.'''
        for entry in entries:
            for block in self.metadata.values():
                if entry[NAME] in block:
                    block[entry[NAME]] = entry
                    break

    def remove_block(self, *names):
        '''Remove a block and all its entries.'''
        for name in names:
            del self.metadata[name]

    def remove_from_block(self, block, *names):
        '''Remove an entry by name from a given block.'''
        for name in names:
            del self.metadata[block][name]

    def remove_from_all(self, *names):
        '''Removes an entry by name, searches for it in all blocks.'''
        for name in names:
            for block in self.metadata.values():
                if name in block:
                    del block[name]
                    break

    def has_block(self, block_name):
        '''Check if metadata has a block with the given name.'''
        if block_name in self.metadata:
            return True
        return False

    def has_entry(self, name):
        '''Check if name is an entry in metadata.'''
        for block in self.metadata.values():
            if name in block:
                return True
        return False

    def find_entry(self, entry_name):
        '''Finds an entry by name and return it and the block it was found in.'''
        for block_name, block in self.metadata.items():
            if entry_name in block:
                return block[entry_name], block_name
        return None, None

    def __str__(self):
        txt = ['---']
        for block_name, block in self.metadata.items():
            txt.append('# ------------------------------------------------------------------------')
            txt.append(f'# {block_name}')
            txt.append('# ------------------------------------------------------------------------')
            for name, doc, value in block.values():
                if doc:
                    txt.extend(doc_wrap(doc))
                txt.append(f'{name}: {value}')
                txt.append('')
            txt.append('')
        txt.append('...\n')
        return '\n'.join(txt)

    def yaml(self):
        '''Returns the metadata as a yaml object.'''
        return yaml.load(str(self))

    def save(self, file_name='metadata.yaml'):
        '''Saves the metadata to file_name.'''
        file_write(file_name, str(self))


class MetadataCollection(object):
    def __init__(self, default_metadata, basic_metadata_includes=None,
                 local_metadata_replaces=None):
        self.default_metadata = default_metadata
        self.basic_metadata_includes = basic_metadata_includes or []
        self.local_metadata_replaces = local_metadata_replaces or []
        self.update_metadata()

    def make_basic_metadata(self):
        if not self.basic_metadata_includes:
            self.basic_metadata = deepcopy(self.default_metadata)
            return

        self.basic_metadata = Metadata()
        for entry_name in self.basic_metadata_includes:
            entry, block_name = self.default_metadata.find_entry(entry_name)
            if self.basic_metadata.has_block(block_name):
                self.basic_metadata.add_to_block(block_name, entry)
            else:
                self.basic_metadata.add_block(block_name, entry)

    def make_local_metadata(self):
        self.local_metadata = deepcopy(self.default_metadata)
        self.local_metadata.replace(*self.local_metadata_replaces)

    def update_metadata(self):
        self.make_basic_metadata()
        self.make_local_metadata()

    def add_to_basic_metadata_includes(self, *entries):
        for entry in entries:
            self.basic_metadata_includes.append(entry)

    def remove_from_basic_metadata_includes(self, *entries):
        for entry in entries:
            self.basic_metadata_includes.remove(entry)

    def replace_in_local_metadata_replaces(self, *entries):
        for entry in entries:
            for index, val in enumerate(self.local_metadata_replaces):
                if entry[NAME] == val[NAME]:
                    self.local_metadata_replaces[index] = entry
                    break

    def add_to_local_metadata_replaces(self, *entries):
        for entry in entries:
            self.local_metadata_replaces.append(entry)

    def remove_from_local_metadata_replaces(self, *names):
        for name in names:
            for val in self.local_metadata_replaces:
                if name == val[NAME]:
                    self.local_metadata_replaces.remove(val)
                    break


DEFAULT_METADATA = Metadata({
    'Metadata': [
        ('title', '', ''),
        ('subtitle', '', ''),
        ('author', '', ''),
        ('publisher', '', ''),
        ('language', '', 'en-US'),
        ('date', '', ''),
        ('identifier', '',
         '\n'
         '  - scheme:\n'
         '  - text:'),
        ('subject', '', ''),
        ('description', '', ''),
    ],

    'Build Informations': [
        ('pandoc-path', 'The path to the pandoc installation', ''),
        ('kindlegen-path', 'The path to kindlegen', ''),
        ('output-formats', 'A list of the formats that should be created by'
                           'runing the build script',
         '\n'
         '  - epub\n'
         '  - pdf'),
    ],

    'Universal Options': [
        ('frontmatter', 'a list of the files that constitute the frontmatter', ''),
        ('backmatter', 'a list of the files that constitute the backmatter', ''),
        ('number-sections', 'should the chapters be auto-numbered?', 'false'),
        ('additional-command-line-options', '', ''),
        ('smart-punctuation', '', ''),
        ('templates-path', '', ''),
        ('input-markdown', 'there are many flavours of markdown. You can '
                           'specify the flavour and pandoc extensions here, '
                           'just as described in the pandoc documentation. '
                           'Probably the most interesting extension would be '
                           '"hard-line-breaks"',
         'markdown'),
        ('markdown-extensions', 'what file extensions should be interpreted as markdown',
         '\n'
         '  - "md"\n'
         '  - "markdown"'),
        ('output-name', 'if you want to give the output file a specific name. '
                        'defaults to title', ''),
        ('other-toc', 'should there be a toc for formats other than epub or pdf?', 'true'),
        ('other-toc-depth', 'how deep should that toc be?', '3'),
        ('date-title', 'include the date in the title', 'false')
    ],

    'Epub Options': [
        ('cover-image', 'the path to the cover image', ''),
        ('frontmatter-heading', 'frontmatter heading (only needed if your '
                                'frontmatter starts without a header, since '
                                'pandoc always creates a header otherwise)',
         'Dedication'),
        ('epub-stylesheet', 'The path to your stylesheet, if you want to '
                            'replace the default stylesheet', ''),
        ('epub-stylesheet-options', '',
         '\n'
         '  heading-alignment: center'),
        ('epub-extra-stylesheet', '', ''),
        ('epub-toc', 'should there be an inline toc?', 'false'),
        ('epub-toc-depth', 'how deep should the toc be?', '3'),
        ('epub-frontmatter', 'a list with the files that constitute the '
                             'frontmatter for epubs (defaults to the universal '
                             'option)', ''),
        ('epub-backmatter', 'a list with the files that constitute the '
                            'backmatter for epubs (defaults to the universal option)',
         ''),
        ('epub-chapter-level', '', '2'),
        ('epub-command-line-options', 'you can add specific pandoc '
                                      'command line options for epubs', ''),
        ('# epub-embed-font', '',
         '\n'
         '#   - name\n'),
        ('epub-pandoc-filter', 'you can use filter for specific formats, '
                               'if you prefix them with the formats short', ''),
    ],

    'PDF Options': [
        ('documentclass', '', 'scrbook'),
        ('panovel-pdf-styles', 'build in environments for latex are found in this files',
         '\n'
         '  - pdf_styles.tex'),
        ('pdf-styles', 'a list of files that contain your custom latex', ''),
        ('paper', 'the trim size of the book that should be created (you '
                  'can use: cm, in, mm or an existing format: legal, letter, '
                  'executive and the ISO formats A, B ,C, D)\n'
                  'Common Paperback sizes: 6in:9in, 5.5in:8.5in, 5.25in:8in, 5in:8in',
         '5.25in:8in'),
        ('BCOR', 'the binding correction (this deepends on the number of '
                 'pages and on the kind of binding)',
         '10mm'),
        ('center-headings', 'change to "true", if chapter headings should be centered',
         'false'),
        ('fontsize', 'the basic fontsize of the book (the size used for paragraphs)',
         '10'),
        ('pdf-toc', 'should there be a toc?', 'true'),
        ('pdf-toc-depth', 'how deep should the toc be?', '3'),
        ('pdf-cover', 'Adds a cover to the pdf. For most print services, this '
                      'should be provided seperatly.', ''),
        ('mainfont', 'this is the standard font', ''),
        ('sansfont', 'this font is used for titles and headings', ''),
        ('monofont', 'this font is used for code and verbatim text', ''),
        ('pdf-frontmatter', 'a list with the files that constitute the '
                            'frontmatter for pdf (defaults to the universal option)',
         ''),
        ('pdf-backmatter', 'a list with the files that constitute the '
                           'backmatter for pdf (defaults to the universal option)',
         ''),
        ('pdf-pandoc-filter', 'you can use filter for specific formats, if you '
                              'prefix them with the formats short', ''),
        ('top-level-division', '', 'chapter'),
        ('pdf-engine', 'one of pdflatex, lualatex, xelatex '
                       '(only xelatex und lualatex support fonts)',
         'xelatex'),
        ('DIV', '', 'calc'),
        ('pagestyle', 'you can chose between two styles for pages:\n'
                      'plain: Just page numbers\n'
                      'headings: The chapter is displayed in the head of the page '
                      '("running headline")',
         'plain'),
        ('headsepline', 'you can seperate the footer with a line', 'false'),
        ('footsepline', 'you can seperate the footer with a line', 'false'),
        ('pdf-command-line-options', 'you can add specific pandoc '
                                     'command line options for pdfs',
         '-V graphics'),
        ('noindent', 'If set to true, paragraphs are not indented anymore '
                     'but seperated by vertical space',
         'false'),
        ('# koma-options', 'Koma script allows many more customizations. '
                           'You can use this variable to add any koma options '
                           'you want to use. Refer to the koma-script '
                           'documentation for what can be done with this',
         '\n'
         '#   - name: headings\n'
         '#     arguments: twolinechapter, big'),
        ('# fontfamilies', 'you can add aditional font-families',
         '\n'
         '#   - name: titlefont # an arbitrary name\n'
         '#     font: Futura'),
        ('# koma-fonts', 'and assign them to specific elements '
                         '(some common elements: title, author, chapter, '
                         'chapterentry, publishers)',
         '\n'
         '#   - element: title\n'
         '#     fontfamily: titlefont'),
    ],

    'HTML Options': [
        ('html-stylesheet', 'The path to your stylesheet, if you want to '
                            'replace the default stylesheet', ''),
        ('html-stylesheet-options', '',
         '\n  # left, right or center\n'
         '  heading-alignment: center'),
        ('html-extra-stylesheet', '', ''),
        ('html-command-line-options', '', '--self-contained')
    ],

    'Markdown Options': [
        ('no-metadata-block-in-output', '', 'true'),
        ('output-markdown', '', 'markdown')
    ],

    'File Data': [
        ('chapter-list', 'Instead of automatically sorting the chapters '
                         'by their filenames, you can here manually sort the files',
         ''),
        ('exclude-files', 'exclude some files if automatically creating the book from files',
         '\n'
         '  - readme.md'),
    ],

    'Filter Options': [
        ('new-scene-style', 'default, text or fleuron', 'default'),
        ('new-scene-text', 'text used for a scene change, if the text option is used. '
                           'If you use symbols, you have to enclose the entry '
                           'with quotation marks.',
         '"* * *"'),
        ('new-scene-image', 'path to the image used for a scene change, '
                            'if fleuron is used as the option', ''),
        ('poem-style', 'bottom, top or one-line', 'bottom'),
        ('quote-style', 'bottom, top or one-line', 'bottom'),
        ('heading-image-level', 'up to which header level the image '
                                'should be included, if the "header-image.py" filter is used',
         '2'),
        ('heading-image', 'path to the image used for a scene change, if '
                          'if the "header-image.py" filter is used', ''),
        ('frontmatter-styles', 'a list of styles that should be moved to the frontmatter',
         '\n'
         '  - frontmatter\n'
         '  - copyrights\n'
         '  - dedication'),
        ('backmatter-styles', 'a list of styles that should be moved to the backmatter',
         '\n'
         '  - backmatter\n'),
    ],

    'Filters': [
        ('panovel-pandoc-filter', 'which build in filters should be used?',
         '\n'
         '  - remove_comments.py\n'
         '  - new_page.py\n'
         '  - dedication.py\n'
         '  - copyrights.py\n'
         '  - epigraph.py\n'
         '  - noindent.py\n'
         '  - alignment.py\n'
         '  - quote.py\n'
         '  - poem.py\n'
         '  - custom_styles.py\n'
         '  - frontmatter.py\n'
         '  - backmatter.py\n'
         '#   - heading_image.py\n'
         '#   - remove_images.py'),
        ('panovel-epub-filter', '',
         '\n'
         '  - epub_remove_fm_head.py'),
        ('panovel-regex-filter', '',
         '\n'
         '  - new_scene.py'),
        ('pandoc-filter', 'you can also write and include your own filters', ''),
        ('regex-filter', '', ''),
        ('epub-filter', '', '')
    ],
})


BASIC_METADATA_INCLUDES = [
    'title', 'subtitle', 'author', 'publisher', 'language', 'date',
    'identifier', 'subject', 'description', 'kindlegen-path', 'output-formats',
    'frontmatter', 'backmatter', 'number-sections', 'cover-image',
    'frontmatter-heading', 'epub-stylesheet-options', 'paper', 'BCOR',
    'center-headings', 'fontsize', 'pdf-toc', 'pdf-toc-depth',
    'new-scene-style', 'new-scene-text', 'new-scene-image', 'poem-style',
    'quote-style', 'heading-image-level', 'heading-image', 'chapter-list',
    'exclude-files'
]


LOCAL_METADATA_REPLACES = [
    ('templates-path', '', './assets/templates/'),
    ('epub-stylesheet', 'The path to your stylesheet, if you want to '
                        'replace the default stylesheet',
     './assets/styles/epub_stylesheet.scss'),
    ('pdf-styles', 'environments for latex are found in this file',
     '\n'
     '  - ./assets/styles/pdf_styles.tex'),
    ('html-stylesheet', 'The path to your stylesheet, if you want to '
                        'replace the default stylesheet',
     './assets/styles/html_stylesheet.scss'),
    ('sass-search-path', '', './assets/styles'),
    ('pandoc-filter', '',
     '\n'
     '  - ./assets/filter/remove_comments.py\n'
     '  - ./assets/filter/new_page.py\n'
     '  - ./assets/filter/dedication.py\n'
     '  - ./assets/filter/copyrights.py\n'
     '  - ./assets/filter/epigraph.py\n'
     '  - ./assets/filter/noindent.py\n'
     '  - ./assets/filter/alignment.py\n'
     '  - ./assets/filter/quote.py\n'
     '  - ./assets/filter/poem.py\n'
     '  - ./assets/filter/custom_styles.py\n'
     '  - ./assets/filter/frontmatter.py\n'
     '  - ./assets/filter/backmatter.py\n'
     '#   - ./assets/filter/heading-image.py\n'
     '#   - ./assets/filter/remove-images.py'),
    ('epub-filter', '',
     '\n'
     '  - ./assets/filter/epub_remove_fm_head.py'),
    ('regex-filter', '',
     '\n'
     '  - ./assets/filter/new_scene.py'),
    ('build-in-pandoc-filter', '', ''),
    ('build-in-epub-filter', '', ''),
    ('build-in-regex-filter', '', '')
]


METADATA = MetadataCollection(DEFAULT_METADATA, BASIC_METADATA_INCLUDES,
                              LOCAL_METADATA_REPLACES)
