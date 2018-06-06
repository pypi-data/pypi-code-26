'''Builds books in different formats out of the files in the book directory'''

import logging
import subprocess
import re
from os import listdir, mkdir, walk
from os.path import join as pjoin
from os.path import relpath, isfile
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from uuid import uuid4
import scss
import yaml
from .utils import (def_get, file_read, file_write, import_script_from_file,
                    change_dir, has_extension)


class BookConversion(object):
    '''This class handles the conversion of the source files into one other
    format.
    '''

    def __init__(self, fmt, cfg):
        self.cfg = cfg
        self.actual_temp_dir = TemporaryDirectory()
        self.temp_dir = self.actual_temp_dir.name
        self.metadata = file_write("metadata.yaml", f"---\n{yaml.dump(cfg)}\n...",
                                   self.temp_dir)

        self.fmt = self.opt_fmt = self.conv_fmt = fmt
        if fmt in ["epub", "epub3"]:
            self.opt_fmt, self.conv_fmt, fmt = "epub", "html", "epub"
        elif fmt in ["pdf", "latex"]:
            self.opt_fmt, self.conv_fmt = "pdf", "latex"
        elif fmt in cfg["markdown-extensions"]:
            self.opt_fmt = "markdown"

        self.output_file = pjoin(cfg['dist-dir'], f'{cfg["output-name"]}.{fmt}')

        self.frontmatter, self.backmatter = [], []
        for matter in ["frontmatter", "backmatter"]:
            if self.cfg_get(f"{self.opt_fmt}-{matter}"):
                setattr(self, matter, cfg[f"{self.opt_fmt}-{matter}"])
            elif self.cfg_get(f"{matter}"):
                setattr(self, matter, cfg[f"{matter}"])

        if self.cfg_get("chapter-list"):
            self.sorted_files = self.cfg["chapter-list"]
        else:
            excluded = self.frontmatter + self.backmatter + self.cfg_get("exclude-files", [])
            self.sorted_files = [name for name in listdir() if name not in excluded
                                 and has_extension(name, self.cfg["markdown-extensions"])]
            self.sorted_files.sort()
        logging.debug(f"Got the file list:\n{self.sorted_files}")

    def make_book(self):
        '''Call all necessary methods to make the book for the format.
        and return the output path if successfull, otherwise None.
        '''
        logging.debug(f"Conversion configuration:\n{self.cfg}")

        self.find_special_matters_styles()
        logging.debug(f"Moved special matter styles.")

        self.regex_transformations()
        logging.debug(f"Regex transformations done.")

        self.make_special_matters()
        logging.debug(f"Made special matters.")

        if not self.run_pandoc():
            return None
        logging.debug(f"Pandoc ran sucessfully.")

        self.post_processing()
        logging.debug(f"Post processing done.")
        return self.output_file

    def find_special_matters_styles(self):
        matter_styles = {
            "frontmatter": self.cfg_get(f"{self.opt_fmt}-frontmatter-styles",
                                        self.cfg_get(f"frontmatter-styles", [])),
            "backmatter": self.cfg_get(f"{self.opt_fmt}-backmatter-styles",
                                       self.cfg_get(f"backmatter-styles", []))
        }

        # pylint: disable=W0631
        def repl(match):
            classes = [x.strip('.') for x in match.group(1).split() if x.startswith('.')]
            if not any(x in matter_styles[matter] for x in classes):
                return match.group(0)

            matter_content = getattr(self, matter)
            matter_content.append(file_write(f'{uuid4()}.md', match.group(0) + '\n',
                                             self.temp_dir))
            setattr(self, matter, matter_content)
            return ''

        block_regex = re.compile(r'~~~{(.*?)}.*?~~~', re.DOTALL)

        new_sorted = []
        for ffile in self.sorted_files:
            text = new_text = file_read(ffile)
            for matter in ['frontmatter', 'backmatter']:
                new_text = block_regex.sub(repl, new_text)
            if text != new_text:
                ffile = file_write(ffile, new_text, self.temp_dir)
            new_sorted.append(ffile)
        self.sorted_files = new_sorted

    def make_special_matters(self):
        '''Preprocess front- and backmatter.'''
        if self.conv_fmt == "html":
            if self.frontmatter and self.opt_fmt == "epub":
                fp = file_write("fm_heading_file.md",
                                f'# {self.cfg["frontmatter-heading"]} {{.unnumbered}}\n',
                                self.temp_dir)
                self.frontmatter.insert(0, fp)
            self.sorted_files = self.frontmatter + self.sorted_files + self.backmatter
            self.frontmatter, self.backmatter = [], []
            return

        filter_cmd_line = self.get_filter_cmd_line()
        for matter in ["frontmatter", "backmatter"]:
            files = getattr(self, matter)
            if not files:
                continue

            new = []
            for ffile in files:
                output = pjoin(self.temp_dir, f"{ffile.rpartition('.')[0]}.{self.conv_fmt}")
                try:
                    subprocess.run(f'pandoc {filter_cmd_line} -o {output} {ffile}',
                                   check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    logging.error(f"Could not convert {matter} for file: {ffile}!")
                else:
                    new.append(output)
            setattr(self, matter, new)

    def run_pandoc(self):
        try:
            subprocess.run(self.get_pandoc_args(), check=True)
            return True
        except subprocess.CalledProcessError:
            logging.error("Pandoc conversion failed!")
            logging.debug(f"Pandoc command-line:\n{self.get_pandoc_args()}!")
            return False
        except FileNotFoundError:
            logging.error('Pandoc not found! Add the path to pandoc to the metadata '
                          'with the option "pandoc_path_: path/to/pandoc"')
            return False

    def get_pandoc_args(self):
        '''Build the pandoc command line.'''
        pandoc_args = ['pandoc -s']

        def add_arg(key, command="", marks=""):
            value = self.cfg.get(key)
            if isinstance(value, list):
                for entry in value:
                    pandoc_args.append(f'{command}{marks}{str(entry)}{marks}')
            elif str(value).lower() == "true":
                pandoc_args.append(command)
            elif str(value).lower() == "false":
                pass
            elif value:
                pandoc_args.append(f'{command}{marks}{str(value)}{marks}')

        add_arg('additional-command-line-options')
        add_arg(f'{self.opt_fmt}-command-line-options')
        add_arg('input-markdown', '-f ')
        if self.fmt == "epub3":
            pandoc_args.append('-t epub3')
        if self.opt_fmt == "markdown":
            add_arg('output-markdown', '-t ')
        if self.opt_fmt == "pdf":
            add_arg('pdf-styles', '-H ', '"')

        # options not recognized in the metadata.yaml and other cases
        add_arg('smart_punctuation_', '-S')
        add_arg('top-level-division', '--top-level-division=')
        add_arg('number-sections', '--number-sections')
        if self.fmt == "pdf":
            add_arg('pdf-engine', '--pdf-engine=')
        if self.opt_fmt == "epub":
            add_arg('epub-embed-font', '--epub-embed-font=', '"')

        # toc related
        prefix = "other" if f'{self.opt_fmt}-toc' not in self.cfg else self.opt_fmt
        add_arg(f'{prefix}-toc', '--toc')
        prefix = "other" if f'{self.opt_fmt}-toc-depth' not in self.cfg else self.opt_fmt
        add_arg(f'{prefix}-toc-depth', '--toc-depth=')

        # back and frontmatter
        for ffile in self.frontmatter:
            pandoc_args.append(f'--include-before-body="{ffile}"')
        for ffile in self.backmatter:
            pandoc_args.append(f'--include-after-body="{ffile}"')

        # template
        if self.cfg_get("templates-path"):
            template_path = pjoin(self.cfg["templates-path"], f'{self.opt_fmt}.template')
            if isfile(template_path):
                pandoc_args.append(f'--template="{template_path}"')

        # stylesheet
        if self.conv_fmt == "html":
            pandoc_args.append(self.get_stylesheet_commandline())

        pandoc_args.append(self.get_filter_cmd_line())
        pandoc_args.append(f'-o "{self.output_file}" "{self.metadata}"')
        for name in self.sorted_files:
            pandoc_args.append(f'"{name}"')
        logging.debug(f"Pandoc command-line arguments:\n{pandoc_args}")
        return ' '.join(pandoc_args)

    def get_filter_cmd_line(self):
        '''Return the filter options for pandoc.'''
        fmt_filter = self.cfg_get(f'{self.opt_fmt}-pandoc-filter', []) +\
            self.cfg_get("pandoc-filter", [])
        if fmt_filter:
            return " ".join([f'--filter="{fil}"' for fil in fmt_filter])
        return ""

    def get_stylesheet_commandline(self):
        '''Return the stylesheet options for pandoc.'''
        if not self.cfg_get(f"{self.opt_fmt}-stylesheet"):
            return ""
        stylesheet = file_read(self.cfg_get(f"{self.opt_fmt}-stylesheet"))

        namespace = scss.namespace.Namespace()
        for var, val in self.cfg_get(f"{self.opt_fmt}-stylesheet-options", {}).items():
            if val[0] == "#":
                namespace.set_variable(f'${var}', scss.types.Color.from_hex(val))
            else:
                namespace.set_variable(f'${var}', scss.types.String(val, None))

        if self.cfg_get(f"{self.opt_fmt}-extra-stylesheet"):
            stylesheet += file_read(self.cfg_get(f"{self.opt_fmt}-extra-stylesheet"))

        css = scss.compiler.compile_string(stylesheet, namespace=namespace,
                                           search_path=[self.cfg_get("sass-search-path")],
                                           output_style='expanded')

        css_file_path = file_write("stylesheet.css", css, self.temp_dir)
        return f'-c {css_file_path}'

    def regex_transformations(self):
        '''Do all regex transformations.'''
        regex_filter = self.cfg_get(f'{self.opt_fmt}-regex-filter', []) +\
            self.cfg_get("regex-filter", [])
        if not regex_filter:
            return

        for files_name in ["sorted_files", "frontmatter", "backmatter"]:
            files = getattr(self, files_name)
            if not files:
                continue

            new_files = []
            for name in files:
                text = new_text = file_read(name)
                for fil in regex_filter:
                    transform = import_script_from_file(fil)
                    new_text = transform.transform(new_text, self.fmt, self.cfg, name)
                if text != new_text:
                    name = file_write(name, new_text, self.temp_dir)
                new_files.append(name)
            setattr(self, files_name, new_files)

    def post_processing(self):
        '''Call the transform function for the format.'''
        if self.opt_fmt == "epub":
            self.epub_transformations()
        elif self.fmt == "html":
            self.html_transformations()
        elif self.opt_fmt == "markdown" and self.cfg.get("no-metadata-block-in-output"):
            self.markdown_transformations()

    def epub_transformations(self):
        '''Transform the epub output.'''
        if not self.cfg_get("epub-filter"):
            return

        # unzip the epub
        unzipped_path = pjoin(self.temp_dir, "unzipped")
        mkdir(unzipped_path)
        with ZipFile(self.output_file) as zf:
            zf.extractall(unzipped_path)

        for name in listdir(unzipped_path):
            if not has_extension(name, "xhtml"):
                continue
            text = new_text = file_read(name, unzipped_path)
            for fil in self.cfg["epub-filter"]:
                transform = import_script_from_file(fil)
                new_text = transform.epub_process(new_text, self.fmt, self.cfg)
            if new_text != text:
                file_write(name, new_text, unzipped_path)

        # rezip the epub file
        with ZipFile(self.output_file, "w") as zf:
            zf.writestr("mimetype", "application/epub+zip")
            for root, _, files in walk(unzipped_path):
                for ffile in files:
                    if "mimetype" in ffile:
                        continue
                    filename = pjoin(root, ffile)
                    arcname = pjoin(relpath(root, unzipped_path), ffile)
                    zf.write(filename, arcname)

    def html_transformations(self):
        '''Transform the html output.'''
        if not self.cfg_get("epub-filter"):
            return

        text = new_text = file_read(self.output_file)
        for fil in self.cfg["epub-filter"]:
            transform = import_script_from_file(fil)
            new_text = transform.epub_process(new_text, self.fmt, self.cfg)
        if new_text != text:
            file_write(self.output_file, new_text)

    def markdown_transformations(self):
        '''Transform the markdwon output.'''
        new_metadata = ""
        if self.cfg_get("title"):
            if self.cfg_get("subtitle"):
                new_metadata = f'{self.cfg["title"]} - {self.cfg["subtitle"]}\n'
            else:
                new_metadata = f'{self.cfg["title"]}\n'
            new_metadata += "===============================================\n\n"
        if self.cfg_get("author"):
            if isinstance(self.cfg["author"], list):
                for author in self.cfg["author"]:
                    new_metadata += f'{author}\n'
            else:
                new_metadata += f'{self.cfg["author"]}\n'
            new_metadata += "\n-----------------------------------------------\n"
        if self.cfg_get("publisher"):
            new_metadata += f'\n{self.cfg["publisher"]}\n'
            new_metadata += "\n-----------------------------------------------\n"

        text = file_read(self.output_file)
        new_text = re.sub(r'^.?---.*?\n---\n', new_metadata, text, flags=re.DOTALL)
        if text != new_text:
            file_write(self.output_file, new_text)

    def cfg_get(self, key, default=None):
        '''Wrapps def_get for use with self.cfg.'''
        return def_get(self.cfg, key, default)


def convert_book(fmt, cfg, class_to_use=BookConversion):
    '''
    Convert to a book in the format 'fmt' using the metadata given by 'cfg'
    '''
    with change_dir(cfg['book-dir']):
        book = class_to_use(fmt, cfg)
        new_book = book.make_book()
    return new_book
