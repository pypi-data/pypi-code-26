#!/usr/bin/env python

"""__main__.py: main entry point for pypodcaster"""

import argparse
import logging
import os
import time
import validators
import yaml
from pkg_resources import get_distribution
from .podcast import Channel

#    pypodcaster: static xml feed generator
#    Copyright (C) 2015-2017 Josh Wheeler
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

__copyright__ = "Copyright 2015-2017 Josh Wheeler"
__license__ = "GPL-3.0"

VERSION = get_distribution('pypodcaster').version


def main():

    sources_list = [os.getcwd()]

    # set up logging

    logging.basicConfig(filename='podcast.log',
                        format='%(levelname)s: %(message)s',
                        filemode="w",
                        level=logging.DEBUG)

    logging.info("Started %s" % time.strftime("%a, %d %b %Y %T %Z"))

    DESCRIPTION = "pypodcaster: static xml feed generator. Copyright (C) 2015-2017 Josh Wheeler. This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For details, visit https://gitlab.com/mantlepro/pypodcaster"

    EPILOG = "example: pypodcaster -o index.xml"

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG)

    parser.add_argument("sources",
                        nargs="*",
                        help="source files or directories",
                        default=sources_list)

    parser.add_argument("-c", "--channel",
                        metavar="/path/to/channel.yml",
                        help="specify channel definition to use instead of current \
                        directory's channel.yml")

    parser.add_argument("-o", "--output",
                        help="output to FILE instead of stdout")

    parser.add_argument('-V', "--version",
                        action="version",
                        version=VERSION)

    args = parser.parse_args()

    if not args.sources == sources_list:
        sources_list = args.sources

    logging.debug("Sources: " + str(sources_list))

    # search for a channel.yml file and open if found. -c or --channel takes
    # precedence; then current directory, and finally specified source
    # directory from args. If a channel.yml is not found, fail with message

    if args.channel:
        options = yaml.safe_load(open(args.channel))
    elif os.path.isfile(os.getcwd() + "/channel.yml"):
        options = yaml.safe_load(open(os.getcwd() + "/channel.yml"))
    elif os.path.isfile(args.sources[0] + "/channel.yml"):
        options = yaml.safe_load(open(args.sources[0] + "/channel.yml"))
    else:
        options = ""
        parser.print_help()
        print("No channel.yml found")
        exit(1)

    def trailing_slash(url):
        """remove trailing slash from url"""
        if url.endswith('/'):
            url = url.rstrip('/')
        return url

    # remove trailing slashes to support either format in channel.yml
    options['podcast_url'] = trailing_slash(options['podcast_url'])

    # determine whether cover image is a url
    try:
        if not validators.url(options.get("image", None)):
            options['image'] = "%s/%s" % (options["podcast_url"],
                                          options.get("image", None))
    except TypeError:
        pass

    # if -o or --output has a value write to it; otherwise, print to stdout

    if args.output:
        with open(args.output, 'w') as output_file:
            output_file.write("%s\n" % Channel(sources_list, options)
                              .render_xml())
    else:
        print(Channel(sources_list, options).render_xml())

    logging.info("Finished %s" % time.strftime("%a, %d %b %Y %T %Z"))


if __name__ == "__main__":
    main()
