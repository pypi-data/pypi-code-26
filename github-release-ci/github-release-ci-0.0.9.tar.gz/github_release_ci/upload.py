#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Upload script."""

import click as cl

from .base import Release


@cl.command()
@cl.option(
    '--destination-filename', '-d',
    default=None,
    help="The file name that should be the asset name at github."
)
@cl.argument("repo_slug")
@cl.argument("release_slug")
@cl.argument("file", type=cl.Path(exists=True))
def main(destination_filename, repo_slug, release_slug, file):
    """Entrypoint."""
    release = Release(repo_slug, release_slug)
    release.upload_asset(file, destination_filename)


if __name__ == '__main__':
    main()
