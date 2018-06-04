'''Project generator for Foliant.'''

from pathlib import Path
from shutil import copytree
from functools import reduce
from string import Template
from logging import DEBUG, WARNING
from typing import List, Dict

from cliar import set_help, set_arg_map, set_metavars
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError

from slugify import slugify

from foliant.utils import spinner
from foliant.cli.base import BaseCli


class BuiltinTemplateValidator(Validator):
    '''Validator for the interactive template selection prompt.'''

    def __init__(self, builtin_templates: List[str]):
        super().__init__()
        self.builtin_templates = builtin_templates

    def validate(self, document):
        '''Check if the selected template exists.'''

        template = document.text

        if template not in self.builtin_templates:
            raise ValidationError(
                message=f'Template {template} not found. '
                + f'Available templates are: {", ".join(self.builtin_templates)}.',
                cursor_position=0
            )


def replace_placeholders(path: Path, properties: Dict[str, str]):
    '''Replace placeholders in a file with the values from the mapping.'''

    with open(path, encoding='utf8') as file:
        file_content = Template(file.read())

    with open(path, 'w', encoding='utf8') as file:
        file.write(file_content.safe_substitute(properties))


class Cli(BaseCli):
    @set_arg_map({'project_name': 'name'})
    @set_metavars({'project_name': 'NAME', 'template': 'NAME or PATH'})
    @set_help(
        {
            'project_name': 'Name of the Foliant project',
            'template': 'Name of a built-in project template or path to custom one',
            'quiet': 'Hide all output accept for the result. Useful for piping.',
            'debug': 'Log all events during project creation. If not set, only warnings and errors are logged.'
        }
    )
    def init(self, project_name='', template='base', quiet=False, debug=False):
        '''Generate new Foliant project.'''

        self.logger.setLevel(DEBUG if debug else WARNING)

        self.logger.info('Project creation started.')

        self.logger.debug(f'Template: {template}')

        template_path = Path(template)

        if not template_path.exists():
            self.logger.debug(
                f'Template not found in {template_path}, looking in installed templates.'
            )

            installed_templates_path = Path(Path(__file__).parent / 'templates')

            installed_templates = [
                item.name for item in installed_templates_path.iterdir() if item.is_dir()
            ]

            self.logger.debug(f'Available templates: {installed_templates}')

            if template in installed_templates:
                self.logger.debug('Template found.')

            else:
                self.logger.debug('Template not found, asking for user input.')

                try:
                    template = prompt(
                        f'Please pick a template from {installed_templates}: ',
                        completer=WordCompleter(installed_templates),
                        validator=BuiltinTemplateValidator(installed_templates)
                    )

                except KeyboardInterrupt:
                    self.logger.warning('Project creation interrupted.')
                    return

            template_path = installed_templates_path / template

            self.logger.debug(f'Template path: {template_path}')

        if not project_name:
            self.logger.debug('Project name not specified, asking for user input.')

            try:
                project_name = prompt('Enter the project name: ')

            except KeyboardInterrupt:
                self.logger.warning('Project creation interrupted.')
                return

        project_slug = slugify(project_name)
        project_path = Path(project_slug)

        properties = {
            'title': project_name,
            'slug': project_slug
        }

        self.logger.debug(f'Project properties: {properties}')

        result = None

        with spinner('Generating project', self.logger, quiet):
            copytree(template_path, project_path)

            text_types = '*.md', '*.yml', '*.txt', '*.py'

            text_file_paths = reduce(
                lambda acc, matches: acc + [*matches],
                (project_path.rglob(text_type) for text_type in text_types),
                []
            )

            for text_file_path in text_file_paths:
                self.logger.debug(f'Processing content of {text_file_path}')
                replace_placeholders(text_file_path, properties)

            for item in project_path.rglob('*'):
                self.logger.debug(f'Processing name of {item}')
                item.rename(Template(item.as_posix()).safe_substitute(properties))

            result = project_path

        if result:
            self.logger.info(f'Result: {result}')

            if not quiet:
                print('─────────────────────')
                print(f'Project "{project_name}" created in {result}')
            else:
                print(result)

        else:
            self.logger.critical('Project creation failed.')
            exit(1)
