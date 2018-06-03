#!/usr/bin/env python

"""podcast.py: essential podcast objects and their functions"""

import logging
import os
import time
from pkg_resources import get_distribution
from time import strftime
import ntpath
import glob
from datetime import datetime
import re
import jinja2
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

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


class Channel:
    """Podcast channel. Sources can be a string or list
    pointing to a one or more directories or mp3 files."""

    def __init__(self, sources, options):
        self.sources = sources
        self.options = options
        self.source_files = []

        for source in sources:
            self.add_files(source)

    def items(self, options):
        """Return all items of the channel newest-to-oldest"""
        all_items = []
        for src in self.source_files:
            all_items.append(Item(src, options))
        logging.debug("Sorting all_items from newest-to-oldest")
        all_items = sorted(
            all_items, key=lambda item: item.sort_date, reverse=True)
        return all_items

    def render_xml(self):
        """render xml template with items"""
        if os.path.isfile(os.getcwd() + "/template.xml"):
            loader = jinja2.FileSystemLoader(os.getcwd())
            logging.debug("Using template from: " + os.getcwd())
        elif os.path.isfile(self.sources[0] + "/template.xml"):
            loader = jinja2.FileSystemLoader(self.sources[0])
            logging.debug("Using template from: " + self.sources[0])
        else:
            # fallback to built-in template in case no template is present
            loader = jinja2.PackageLoader("pypodcaster", 'templates')
            logging.debug("Using default template")
        env = jinja2.Environment(loader=loader)
        template_xml = env.get_template('template.xml')
        # set up template variables
        return template_xml.render(
            channel=self.options,
            items=self.items(self.options),
            last_build_date=strftime("%a, %d %b %Y %T %Z"),
            generator="pypodcaster " + get_distribution('pypodcaster').version
        )

    def add_files(self, source):
        """add absolute paths to source_files"""
        if os.path.isdir(source):
            logging.debug(source + " is directory")
            os.chdir(source)
            for file in glob.glob("*.mp3"):
                self.source_files.append("%s/%s" % (os.getcwd(), file))
                logging.debug
                ("Adding %s/%s to source_files" % (os.getcwd(), file))
        else:
            self.source_files.append(source)
            logging.debug("Adding %s to source_files" % source)


class Item:
    """Item object containing vars related to id3 tag"""

    def __init__(self, file_path, options):
        if file_path.endswith('.mp3'):
            id3 = EasyID3(file_path)
            audio = MP3(file_path)
            if 'title' in id3:
                self.title = ''.join(id3['title'])
            else:
                self.title = ''
            if 'album' in id3:
                self.album = ''.join(id3['album'])
            else:
                self.album = ''
            # TODO: add ability for user to add description through id3 tag
            self.comment = ""
            if 'artist' in id3:
                self.artist = ''.join(id3['artist'])
            else:
                self.artist = ''
            self.subtitle = options.get("subtitle")
            self.url = "%s/%s" % (options.get("podcast_url"),
                                  ntpath.basename(file_path))
            self.sort_date = self.get_date(file_path)
            # set pub_date to RFC 822 format (Sat, 07 Sep 2002 0:00:01 GMT)
            self.pub_date = self.sort_date.strftime(
                "%a, %d %b %Y %T ") + time.strftime('%Z')
            self.length = os.stat(file_path).st_size
            self.seconds = audio.info.length
            self.duration = time.strftime(
                '%M:%S', time.gmtime(float(self.seconds)))

    def get_date(self, filename):
        """Extract pub_date from filename containing YYYY-MM-DD
        or else use file's modified time as a fallback."""
        date = datetime.fromtimestamp(os.stat(filename).st_mtime)
        dashless_date = re.search(r'(\d{4}\d{2}\d{2})', filename)
        dashed_date = re.search(r'(\d{4}\-\d{2}\-\d{2})', filename)
        try:
            if dashless_date:
                date = datetime.strptime(dashless_date.group(0), "%Y%m%d")
            elif dashed_date:
                date = datetime.strptime(dashed_date.group(0), "%Y-%m-%d")
        except ValueError as err:
            logging.error(
                "Filename contains incorrect date: %s %s" % (
                    filename,
                    str(err)
                )
            )
            logging.info("Using file's mtime for " + filename)
        return date

    def get_image_url(self, file_path, options, title, album):
        """check for episodic image with similar name or add channel default"""

        files = os.listdir(os.path.dirname(file_path))
        mp3file = os.path.basename(file_path)
        image_guess = os.path.splitext(mp3file)[0] + ".jpg"
        found = False

        for file in files:
            if file.lower() == image_guess.lower():
                logging.info(
                    "Episodic image found for %s using filename." % mp3file)
                image_url = "%s/%s" % (options["podcast_url"], file)
                found = True
                break
            elif os.path.isfile(title + ".jpg"):
                logging.info(
                    "Episodic image found for %s using title tag" % mp3file)
                image_url = "%s/%s" % (options["podcast_url"], title + ".jpg")
                found = True
                break
            elif os.path.isfile(title.lower() + ".jpg"):
                logging.info(
                    "Episodic image found for %s using lowercase title tag"
                    % mp3file)
                image_url = "%s/%s" % (
                    options["podcast_url"], title.lower() + ".jpg")
                found = True
                break
            elif os.path.isfile(album + ".jpg"):
                logging.info(
                    "Episodic image found for %s using album tag" % mp3file)
                image_url = "%s/%s" % (options["podcast_url"], album + ".jpg")
                found = True
                break
            elif os.path.isfile(album.lower() + ".jpg"):
                logging.info(
                    "Episodic image found for %s using album lowercase tag"
                    % mp3file)
                image_url = "%s/%s" % (
                    options["podcast_url"],
                    album.lower() + ".jpg")
                found = True
                break

        if not found:
            logging.debug(
                "No episodic image found for %s. Using channel default image."
                % mp3file)
            image_url = options.get("image", None)

        return image_url

        self.image_url = self.get_image_url(
            file_path, options, self.title, self.album)
