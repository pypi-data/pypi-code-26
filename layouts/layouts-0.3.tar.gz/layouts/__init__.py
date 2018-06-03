'''
Python API for HID-IO HID Layouts Repository

- Allows querying from a GitHub cache (or internal cache)
- Handles JSON merging
- Can query all possible layouts


Call using python virtual env + python -m layouts

1) cd layouts.git
2) pipenv install
3) pipenv shell
4) python -m layouts --help
'''

## Imports

import argparse
import glob
import json
import logging
import os
import shutil
import tarfile
import tempfile

import requests

from github import Github


## Variables

__version__ = '0.3'

log = logging.getLogger(__name__)


## Classes

class Layouts:
    '''
    Retrieves various HID layouts using an external cache.

    If no cache is found, one is downloaded from GitHub.
    By default, when retrieving a cache from GitHub, the latest version is used.
    '''
    def __init__(self,
        github_path='hid-io/layouts',
        version='master',
        force_refresh=False,
        cache_dir=tempfile.gettempdir(),
        token=None,
        layout_path=None,
    ):
        '''
        @param github_path: Location of the git repo on GitHub (e.g. hid-io/layouts)
        @param version: git reference for the version to download (e.g. master)
        @param force_refresh: If True, always check GitHub for the latest cache
        @param cache_dir: Directory to operate on external cache from
        @param token: GitHub access token, defaults to None
        @param layout_path: Location to look for layouts (e.g. local copy). Disables GitHub cache when not None.
        '''
        self.layout_path = layout_path

        # Only check GitHub cache if layout_path is not set
        if self.layout_path is None:
            # Check to see if there is a cache available already
            match = "*{}*".format(github_path.replace('/', '-'))
            matches = sorted(glob.glob(os.path.join(cache_dir, match)))

            # If force refresh, clear cache, and return no matches
            if force_refresh:
                for mat in matches:
                    shutil.rmtree(mat)
                matches = []

            # No cache, retrieve from GitHub
            if not matches:
                self.retrieve_github_cache(github_path, version, cache_dir, token)
                matches = sorted(glob.glob(os.path.join(cache_dir, match)))

            # Select the newest cache
            self.layout_path = matches[-1]

        # Scan for all JSON files
        self.json_file_paths = sorted(glob.glob(os.path.join(self.layout_path, "**/*.json")))

        # Load each of the JSON files into memory
        self.json_files = {}
        for path in self.json_file_paths:
            with open(path) as json_file:
                self.json_files[path] = json.load(json_file)

        # Query names for all of the layouts
        self.layout_names = {}
        for json_file, json_data in self.json_files.items():
            for name in json_data['name']:
                self.layout_names[name] = json_file

    def retrieve_github_cache(self, github_path, version, cache_dir, token):
        '''
        Retrieves a cache of the layouts git repo from GitHub

        @param github_path: Location of the git repo on GitHub (e.g. hid-io/layouts)
        @param version: git reference for the version to download (e.g. master)
        @param cache_dir: Directory to operate on external cache from
        @param token: GitHub access token
        '''
        # Check for environment variable Github token
        token = os.environ.get('GITHUB_APIKEY', None)

        # Retrieve repo information
        gh = Github(token)
        repo = gh.get_repo(github_path)
        commit = repo.get_commit(version)
        commits = repo.get_commits()
        total_commits = 0
        commit_number = 0
        for cmt in commits:
            if commit == cmt:
                commit_number = total_commits
            total_commits += 1
        commit_number = total_commits - commit_number
        tar_url = repo.get_archive_link('tarball', commit.sha)
        # GitHub only uses the first 7 characters of the sha in the download
        dirname_orig = "{}-{}".format(github_path.replace('/', '-'), commit.sha[:7])
        dirname_orig_path = os.path.join(cache_dir, dirname_orig)
        # Adding a commit number so it's clear which is the latest version without requiring git
        dirname = "{}-{}".format(commit_number, dirname_orig)
        dirname_path = os.path.join(cache_dir, dirname)

        # If directory doesn't exist, check if tarball does
        if not os.path.isdir(dirname_path):
            filename = "{}.tar.gz".format(dirname)
            filepath = os.path.join(cache_dir, filename)

            # If tarball doesn't exist, download it
            if not os.path.isfile(filepath):
                # Retrieve tar file
                chunk_size = 2000
                req = requests.get(tar_url, stream=True)
                with open(filepath, 'wb') as infile:
                    for chunk in req.iter_content(chunk_size):
                        infile.write(chunk)

            # Extract tarfile
            tar = tarfile.open(filepath)
            tar.extractall(cache_dir)
            os.rename(dirname_orig_path, dirname_path)

            # Remove tar.gz
            os.remove(filepath)

    def list_layouts(self):
        '''
        Returns a list of all defined names/aliases for HID layouts
        '''
        return sorted(list(self.layout_names.keys()))

    def get_layout(self, name):
        '''
        Returns the layout with the given name
        '''
        layout_chain = []

        # Retrieve initial layout file
        json_data = self.json_files[self.layout_names[name]]
        layout_chain.append(Layout(name, json_data))

        # Recursively locate parent layout files
        parent = layout_chain[-1].parent()
        while parent is not None:
            # Find the parent
            parent_path = None
            for path in self.json_file_paths:
                if parent in path:
                    parent_path = path

            # Make sure a path was found
            if parent_path is None:
                raise UnknownLayoutPathException('Could not find: {}'.format(parent_path))

            # Build layout for parent
            json_data = self.json_files[parent_path]
            layout_chain.append(Layout(parent_path, json_data))

            # Check parent of parent
            parent = layout_chain[-1].parent()

        # Squash layout files
        layout = self.squash_layouts(layout_chain)
        return layout

    def dict_merge(self, merge_to, merge_in):
        '''
        Recursively merges two dicts

        Overwrites any non-dictionary items
        merge_to <- merge_in
        Modifies merge_to dictionary

        @param merge_to: Base dictionary to merge into
        @param merge_in: Dictionary that may overwrite elements in merge_in
        '''
        for key, value in merge_in.items():
            # Just add, if the key doesn't exist yet
            # Or if set to None/Null
            if key not in merge_to.keys() or merge_to[key] is None:
                merge_to[key] = value
                continue

            # Overwrite case, check for types
            # Make sure types are matching
            if not isinstance(value, type(merge_to[key])):
                raise MergeException('Types do not match! {}: {} != {}'.format(key, type(value), type(merge_to[key])))

            # Check if this is a dictionary item, in which case recursively merge
            if isinstance(value, dict):
                self.dict_merge(merge_to[key], value)
                continue

            # Otherwise just overwrite
            merge_to[key] = value

    def squash_layouts(self, layouts):
        '''
        Returns a squashed layout

        The first element takes precedence (i.e. left to right).
        Dictionaries are recursively merged, overwrites only occur on non-dictionary entries.

        [0,1]

        0:
        test: 'my data'

        1:
        test: 'stuff'

        Result:
        test: 'my data'

        @param layouts: List of layouts to merge together
        @return: New layout with list of layouts squash merged
        '''
        top_layout = layouts[0]
        json_data = {}

        # Generate a new container Layout
        layout = Layout(top_layout.name(), json_data, layouts)

        # Merge in each of the layouts
        for mlayout in reversed(layouts):
            # Overwrite all fields, *except* dictionaries
            # For dictionaries, keep recursing until non-dictionaries are found
            self.dict_merge(layout.json(), mlayout.json())

        return layout


class UnknownLayoutPathException(Exception):
    '''
    Thrown when an unknown layout path is used
    '''
    pass


class ComposeException(Exception):
    '''
    Thrown when a Layout composition is not possible with a given layout.
    '''
    pass


class MergeException(Exception):
    '''
    Thrown when an unexpected merge situation arises.
    Usually when the item types differ.
    '''
    pass


class Layout:
    '''
    Container class for each JSON layout dictionary.

    Includes some convenience functions that are useful with composition.
    '''
    def __init__(self, name, json_data, parents=None):
        '''
        @param name: Name used to define layout
        @param json_data: JSON data for layout
        @param parents: List of parent Layout objects when doing a squash merge
        '''
        self.layout_name = name
        self.json_data = json_data
        self.json_data_orig = json_data
        self.parents = parents

    def name(self):
        '''
        Name attributed to the layout initially

        To get all possible names, use self.json_data['name'] instead.

        @return: Attributed name for the layout
        '''
        return self.layout_name

    def json(self):
        '''
        Returns a JSON dictionary for the layout

        @return: JSON data for layout
        '''
        return self.json_data

    def json_orig(self):
        '''
        Returns the original JSON dictionary for the layout (exludes squashing)

        @return: Original JSON data for layout
        '''
        return self.json_data_orig

    def locale(self):
        '''
        Do a lookup for the locale code that is set for this layout.

        NOTE: USB HID specifies only 35 different locales. If your layout does not fit, it should be set to Undefined/0

        @return: Tuple (<USB HID locale code>, <name>)
        '''
        name = self.json_data['hid_locale']

        # Set to Undefined/0 if not set
        if name is None:
            name = "Undefined"

        return (int(self.json_data['from_hid_locale'][name]), name)

    def __repr__(self):
        '''
        String representation of Layout
        '''
        return "Layout(name={})".format(self.layout_name)

    def parent(self):
        '''
        Returns the parent file of the layout

        @returns: Parent file of layout, None if there is none.
        '''
        return self.json_data['parent']

    def compose(self, text, minimal_clears=False):
        '''
        Returns the sequence of combinations necessary to compose given text.

        If the text expression is not possible with the given layout an ComposeException is thrown.

        Iterate over the string, converting each character into a key sequence.
        Between each character, an empty combo is inserted to handle duplicate strings (and USB HID codes between characters)

        @param text: Input UTF-8 string
        @param minimal_clears: Set to True to minimize the number of code clears. False (default) includes a clear after every character.

        @returns: Sequence of combinations needed to generate the given text string
        '''
        sequence = []

        for char in text:
            # Make sure the composition element is available
            if char not in self.json_data['composition']:
                raise ComposeException("'{}' is not defined as a composition in the layout '{}'".format(char, self.name))

            # Lookup the sequence to handle this character
            lookup = self.json_data['composition'][char]

            # If using minimal clears, check to see if we need to re-use any codes
            # Only need to check the most recent addition with the first combo
            if sequence and set(tuple(lookup[0])) & set(tuple(sequence[-1])):
                sequence.extend([[]])

            # Add to overall sequence
            sequence.extend(lookup)

            # Add empty combo for sequence splitting
            if not minimal_clears:
                # Blindly add a clear combo between characters
                sequence.extend([[]])

        # When using minimal clears, we still need to add a final clear
        if minimal_clears:
            sequence.extend([[]])

        return sequence



## Functions

def main(argv=None):
    '''
    Main entry-point for calling layouts directly as a program.
    '''
    # Prep argparse
    ap = argparse.ArgumentParser(
        description='Basic query options for Python HID-IO Layouts repository',
    )
    ap.add_argument('--list', action='store_true', help='List available layout aliases.')
    ap.add_argument('--get', metavar='NAME', help='Retrieve the given layout, and return the JSON data')

    # Parse arguments
    args = ap.parse_args(argv)

    # Create layouts context manager
    mgr = Layouts()

    # Check if generating a list
    if args.list:
        for name in mgr.list_layouts():
            print(name)

    # Retrieve JSON layout
    if args.get is not None:
        layout = mgr.get_layout(args.get)
        print(json.dumps(layout.json()))

