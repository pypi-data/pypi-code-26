#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Github Release asset download script."""

from os import getcwd
import click as cl

from .base import Release


@cl.command()
@cl.option("--out", "-o", default=getcwd(), help="Download destination path")
@cl.argument("repo_slug")
@cl.argument("release_slug")
def main(out, repo_slug, release_slug):
    """Entrypoint."""
    release = Release(repo_slug, release_slug)
    release.download_assets(out)


if __name__ == '__main__':
    main()
