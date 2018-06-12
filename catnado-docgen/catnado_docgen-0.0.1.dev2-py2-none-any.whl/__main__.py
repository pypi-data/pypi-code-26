import argparse

from build import main as build_main


BUILD_IGNORE_HELP = 'List of path substrings to ignore'
BUILD_OUTPUT_TARGET_HELP = 'mkdocs.yml file or output directory for markdown files'
BUILD_PAGES_HELP = 'Update provided mkdocs.yml file with new pages entries for newly-written files'
BUILD_PRINT_HELP = 'Print the provided mkdocs.yml changes so you can add them yourself'
BUILD_PACKAGE_HELP = 'Name of top Python package to document (must be importable)'


def main():
  parser = argparse.ArgumentParser()

  subparsers = parser.add_subparsers()

  build_subparser = subparsers.add_parser('build')
  build_subparser.add_argument('root_package', help=BUILD_PACKAGE_HELP)
  build_subparser.add_argument('output_target', help=BUILD_OUTPUT_TARGET_HELP)
  pages_mutex_group = build_subparser.add_mutually_exclusive_group()
  pages_mutex_group.add_argument('--update-pages', action='store_true',
      help=BUILD_PAGES_HELP)
  pages_mutex_group.add_argument('--print-pages', action='store_true',
      help=BUILD_PRINT_HELP)

  build_subparser.set_defaults(func=build_main)

  args = parser.parse_args()
  args.func(args)
