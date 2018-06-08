'''The console script'''

import logging
import sys
import subprocess
import platform
import re
from os import mkdir, makedirs, chdir, getcwd, listdir
from os.path import join as pjoin
from os.path import dirname, isdir, normpath, abspath, isfile
from shutil import copytree, copyfile
from argparse import ArgumentParser
from pkg_resources import resource_filename
import yaml
from .book_conversion import convert_book, BookConversion
from .metadata import METADATA
from .utils import def_get, file_write, file_read, change_dir, is_markdown_file


class ConsoleScript(object):
    '''Creates the console script commands'''

    def __init__(self, package_name, conversion_class=BookConversion,
                 metadata=METADATA, provided_defaults=None):
        self.package_name = package_name
        self.conversion_class = conversion_class
        self.metadata = metadata
        if provided_defaults is None:
            self.provided_defaults = []
        elif provided_defaults == ["all"]:
            self.provided_defaults = ["templates-path", "sass-search-path",
                                      "epub-stylesheet", "html-stylesheet"]
        else:
            self.provided_defaults = provided_defaults
        self.cfg = {}
        self.args = None
        self.single_file_mode = False

    def run(self):
        '''Run the command line script'''
        parser = self.make_parser('Create books out of markdown files in the book folder')
        self.args = parser.parse_args()

        # logging
        logging.basicConfig(format='%(levelname)s: %(message)s',
                            level=getattr(logging, self.args.log))

        with change_dir(self.args.source):
            self.run_command()

    def make_parser(self, description=""):
        parser = ArgumentParser(description=description)
        parser.add_argument('project_name', nargs='?', default=None,
                            help='Make a new project directory with the given name. '
                                 'If no name is given, run the conversion process.')
        parser.add_argument('-l', '--local-copy', action='store_true',
                            help='Creates all filters, styles, templates etc. in'
                                 'the local folder')
        parser.add_argument('-c', '--create-metadata-file', action='store_true',
                            help='Creates a full metadata.yaml file. Can be used '
                                 'stand alone or while making a new project.')
        parser.add_argument('-f', '--formats', nargs='*', default=[],
                            choices=["epub", "pdf", "md", "epub3", "latex", "html"],
                            help='The formats that should be produced.')
        parser.add_argument('-s', '--source', nargs='?', default=getcwd(),
                            help='Path to the book directory. '
                                 'Defaults to the current directory')
        parser.add_argument('-t', '--target', nargs='?', default="dist",
                            help='The target directory for the build books. '
                                 'Defaults to "dist" inside the source folder')
        parser.add_argument('-o', '--output-name', nargs='?', default="",
                            help='The name of the output file. '
                                 'Defaults to the title')
        parser.add_argument('-m', '--metadata', nargs='?', default="metadata.yaml",
                            help='Path to the metadata file that should be used. '
                                 'Defaults to "metadata.yaml"')
        parser.add_argument('--single-files', action='store_true',
                            help='Instead of one folder consisting of one book, '
                                 'each file in the source folder is considered a book. '
                                 'This is only needed, if multiple single books '
                                 'are in one directory. '
                                 'Accepts a single file as an argument for source.')
        parser.add_argument('--no-git', action='store_true',
                            help='Do not create a git repository.')
        parser.add_argument('--log', nargs='?', default="INFO",
                            choices=["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"],
                            help='The logging level. '
                                 'Defaults to "INFO"')
        return parser

    def run_command(self):
        if self.args.project_name:
            self.new_project()
        elif self.args.create_metadata_file:
            self.create_metadata_file()
        elif self.args.single_files:
            self.make_single_file_books()
        else:
            self.make_books()

    def make_books(self):
        '''Build the book files.'''
        logging.info('Starting conversion process.')

        # setup config
        self.get_configuration()
        self.set_config_defaults()

        # some pre work
        self.pre_convert()

        # create the book files
        self.convert_books()

    def make_single_file_books(self):
        self.single_file_mode = True
        logging.info('Singel file mode')

        if isdir(self.args.source):
            book_files = [ffile for ffile in listdir() if is_markdown_file(ffile)]
        else:
            book_files = [self.args.source]

        for book_file in book_files:
            self.book_file = book_file
            self.make_books()

    def get_configuration(self):
        '''
        Get the metadata informations from the default metadata and the user
        suplied metadata.
        '''
        self.cfg = self.metadata.default_metadata.yaml()

        # check if only a single file is in the book folder
        if not self.single_file_mode:
            book_files = [ffile for ffile in listdir() if is_markdown_file(ffile)]
            if len(book_files) == 1:
                self.single_file_mode = True
                self.book_file = book_files[0]

        # get the options
        if isfile(self.args.metadata):
            self.cfg.update(yaml.load(file_read(self.args.metadata)))
        elif not self.single_file_mode:
            logging.warning('No metadata file found!')

        # in single file mode, get the metadata from the file
        if self.single_file_mode:
            md = re.match(r'.?-{3}(.*?)(\n\.{3}\n|\n-{3}\n)',
                          file_read(self.book_file), re.DOTALL)
            if md:
                self.cfg.update(yaml.load(md.group(1)))
            elif not isfile(self.args.metadata):
                logging.warning('No metadata found in the file!')

    def set_config_defaults(self):
        '''Set the given default paths for stylesheets, filter etc.'''
        def set_default(name, resource):
            package_name = self.package_name if name in self.provided_defaults else "panovel"
            self.cfg[name] = def_get(self.cfg, name, resource_filename(package_name, resource))

        def set_default_list(opt, resource):
            self.cfg[opt] = def_get(self.cfg, opt, [])
            self.cfg[opt].extend(
                [resource_filename("panovel", f'{resource}/{x}')
                 for x in def_get(self.cfg, f"panovel-{opt}", [])])
            if self.package_name != "panovel" and f"{self.package_name}-{opt}" in self.cfg:
                self.cfg[opt].extend(
                    [resource_filename(self.package_name, f'{resource}/{x}')
                     for x in self.cfg[f"{self.package_name}-{opt}"]])

        set_default("templates-path", "templates")
        set_default("sass-search-path", "styles")
        set_default("epub-stylesheet", "styles/epub_stylesheet.scss")
        set_default("html-stylesheet", "styles/html_stylesheet.scss")
        set_default_list("pdf-styles", "styles")
        set_default_list("pandoc-filter", "filter")
        set_default_list("epub-filter", "filter")
        set_default_list("regex-filter", "filter")

    def pre_convert(self):
        if self.args.output_name:
            self.cfg["output-name"] = self.args.output_name
        elif not self.cfg.get("output-name"):
            self.cfg["output-name"] = self.cfg["title"]
        self.cfg["dist-dir"] = self.args.target
        self.cfg["book-dir"] = self.args.source

        if not isdir(self.args.target):
            makedirs(self.args.target)
            logging.info('Created destination folder.')

        if self.cfg.get("pandoc-path"):
            sys.path.append(abspath(dirname(self.cfg["pandoc-path"])))
            logging.debug('Added pandoc to PATH.')

        if self.single_file_mode:
            self.cfg['chapter-list'] = [self.book_file]

    def convert_books(self):
        formats = set(self.args.formats) if self.args.formats else set(self.cfg["output-formats"])

        # kindle specific actions
        kindle = False
        for x in ["kindle", "mobi"]:
            if x in formats:
                formats.remove(x)
                formats.add("epub")
                kindle = True

        # create the book files
        for fmt in formats:
            logging.info(f'Building {self.cfg.get("output-name")} as {fmt}')
            output_path = convert_book(fmt, self.cfg, self.conversion_class)
            if output_path:
                logging.info(f'Produced {fmt} book: {output_path}')
            else:
                logging.error(f"Could not produce {fmt} book!")

        # create kindle file
        if kindle:
            logging.info(f'Building kindle book')
            if self.cfg.get("kindlegen-path"):
                kindlegen_path = normpath(self.cfg["kindlegen-path"])
            else:
                kindlegen_path = "kindlegen"
            try:
                epub_path = pjoin(self.args.target, f'{self.cfg["output-name"]}.epub')
                subprocess.run(f'"{kindlegen_path}" "{epub_path}"', check=True)
            except FileNotFoundError:
                logging.error("Kindlegen not found! - No kindle file created.")
            else:
                logging.info(f'Produced kindle book.')

    def new_project(self):
        '''Make a new project directory.'''
        mkdir(self.args.project_name)
        chdir(self.args.project_name)
        mkdir('images')
        mkdir('dist')

        metadata = self.metadata.basic_metadata if not self.args.create_metadata_file \
            else self.metadata.default_metadata

        if self.args.local_copy:
            metadata = self.metadata.local_metadata
            self.copy_local_files()

        metadata.save()

        # on windows create a bat file to easily run the script
        if platform.system() == 'Windows':
            file_write('build_book.bat', f'{self.package_name}\npause\n')

        # if git is installed, initialize it
        if not self.args.no_git:
            try:
                subprocess.run("git init")
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            else:
                copyfile(resource_filename(self.package_name, 'templates/gitignore.template'),
                         '.gitignore')
                subprocess.run("git add .")
                subprocess.run('git commit -q -m "Initial commit"')
        logging.info(f'Created new project.')

    def copy_local_files(self):
        copytree(resource_filename("panovel", "styles"), 'assets/styles')
        copytree(resource_filename("panovel", "templates"), 'assets/templates')
        copytree(resource_filename(self.package_name, "filter"), 'assets/filter')
        if self.package_name != "panovel":
            copytree(resource_filename(self.package_name, "styles"), 'assets/styles')
            copytree(resource_filename(self.package_name, "templates"), 'assets/templates')
            cfg = self.metadata.default_metadata.yaml()
            for fil in ['panovel-pandoc-filter', 'panovel-epub-filter', 'panovel-regex-filter']:
                for fname in def_get(cfg, fil, []):
                    copyfile(resource_filename('panovel', f'filter/{fname}'),
                             f'assets/filter/{fname}')

    def create_metadata_file(self):
        '''Create a full metadata file in the book directory.'''
        self.metadata.default_metadata.save('full_metadata.yaml')
        logging.info(f'Created full metadata.')


def run_script(package_name="panovel", conversion_class=BookConversion,
               console_class=ConsoleScript, metadata=METADATA, provided_defaults=None):
    '''
    Runs the console script, needs the package name. Optionally a different
    conversion object can be given and another console_class object.

    provided_defaults is a list containing the names of the ressources given by
    the package. For defaults not given here, panovels defaults are used.

    metadata is an object of the type MetadataCollection that collects the
    default_, basic_ and local_metadata.

    Here a complete list of possible defaults for provided_defaults:
    ["templates-path", "sass-search-path", "epub-stylesheet", "html-stylesheet"]
    or simply ["all"], if all are provided by the package.
    '''
    script = console_class(package_name, conversion_class, metadata, provided_defaults)
    script.run()
