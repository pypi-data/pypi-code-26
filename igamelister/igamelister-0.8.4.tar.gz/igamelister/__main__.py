import logging
import logging.config
import os
import sys
from pathlib import Path

import click
import coloredlogs
# noinspection PyPackageRequirements
import progressbar

from igamelister.cli.config import Config
from igamelister.cli.igame import Igame
from igamelister.cli.packages import Packages
from igamelister.cli.slaves import Slaves

DATA_DIR = ".igamelister"

progressbar.streams.wrap_stderr()
logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG)


@click.group()
@click.option("-v", "--verbose", count=True, help="Increase verbosity of console output.")
@click.option("-q", "--quiet", is_flag=True, help="Suppress all console output. Overrides verbose option.")
@click.option("-o", "--out", default=None, type=click.Path(exists=False), help="Write all logging output to a file.")
@click.version_option(prog_name="iGameLister")
@click.pass_context
def cli(ctx, verbose, quiet, out):
    """iGameLister - A tool to generate nicely formatted 'gameslist' and 'genre' files for iGame
    (http://winterland.no-ip.org/igame/), an AmigaOS WHDLoad launcher application.

    Data files for WHDLoad Package information (packages.dat) and local WHDLoad Slaves (slaves.dat) are saved to the
    .igamelister directory in your OS user home path.
    """
    def get_data_dir() -> Path:
        home_dir = Path.home()
        data_dir = Path(os.path.join(home_dir, DATA_DIR))
        if not data_dir.exists():
            data_dir.mkdir()
            return data_dir
        else:
            if not data_dir.is_dir():
                raise FileExistsError(f"'{data_dir}' exists, but is not a directory.")
            else:
                return data_dir

    ctx.obj = Config(get_data_dir(), verbose, quiet, out)

    if ctx.obj.out is not None:
        loggers_handlers = ["file", "console"]
        handlers = {
            "console": {
                "formatter": "console",
                "level": ctx.obj.verbosity,
                "class": "logging.StreamHandler",
            },
            "file": {
                "formatter": "verbose",
                "level": logging.DEBUG,
                "class": "logging.FileHandler",
                "filename": ctx.obj.out,
            },
        }
    else:
        loggers_handlers = ["console"]
        handlers = {
            "console": {
                "formatter": "console",
                "level": ctx.obj.verbosity,
                "class": "logging.StreamHandler",
            },
        }

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
            "console": {
                "()": "coloredlogs.ColoredFormatter",
                # "format": "%(message)s",
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                # "format": "[%(levelname)s] %(message)s",
            },
        },
        "handlers": handlers,
        "loggers": {
            "": {
                "handlers": loggers_handlers,
                "level": logging.DEBUG,
                "propagate": True,
            },
        },
    })


#
# Top level command groups
#


@cli.group("igame", short_help="Create iGame configuration files.")
def igame():
    """Create iGame configuration files from information in iGameLister data files.
    """
    pass


@cli.group("packages", short_help="Manage WHDLoad Package data file.")
def packages():
    """Manage the iGameLister WHDLoad Package data file (packages.dat).
    Information is collected from the following websites:

    \b
    WHDLoad (http://www.whdload.de/)
    Hall Of Light (http://hol.abime.net/)
    Lemon Amiga (http://www.lemonamiga.com/)
    Amiga Demoscene Archive (http://ada.untergrund.net/)
    Kestra BitWorld (http://janeway.exotica.org.uk/)
    Pouët (http://www.pouet.net/)
    """
    pass


@cli.group("slaves", short_help="Manage WHDLoad Slave data file.")
def slaves():
    """Manage the iGameLister WHDLoad Slave data file (slaves.dat).
    Information is collected from local WHDLoad Slave files.
    """
    pass


#
# Slaves commands
#


@slaves.group("add", short_help="Add WHDLoad Slaves.")
def slaves_add():
    """Add information from local WHDLoad Slave files to the iGameLister WHDLoad Slave data file (slaves.dat).
    """
    pass


@slaves.command("details", short_help="Show info for a WHDLoad Slave.")
@click.argument("slave_id", type=int)
@click.pass_context
def slaves_details(ctx, slave_id):
    """Show information for a WHDLoad Slave in the iGameLister WHDLoad Slave data file (slaves.dat) that has an ID
    matching SLAVE_ID.
    """
    data = Slaves(ctx)
    data.load()
    try:
        data.cli_slaves_details(slave_id)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")


@slaves.command("find", short_help="Find WHDLoad Slaves.")
@click.argument("filter-text")
@click.option("-s", "--sort-by",
              type=click.Choice(["id", "date", "dir", "file", "name"]),
              help="Sort the list of WHDLoad Slaves.")
@click.pass_context
def slaves_find(ctx, filter_text, sort_by):
    """Display a list of all WHDLoad Slaves in the iGameLister WHDLoad Slave data file (slaves.dat) that include
    FILTER_TEXT in the installed WHDLoad package path.

    The list of WHDLoad Slaves can be sorted by the following criteria:

    \b
      id: The ID number of the WHDLoad Slaves. (default)
    date: The file date of the WHDLoad Slaves.
     dir: The installed directory of the WHDLoad Slaves.
    file: The file name of the WHDLoad Slaves.
    name: The internal name of the WHDLoad Slaves.
    """
    data = Slaves(ctx)
    data.load()
    try:
        data.cli_slaves_find(filter_text, sort_by)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")


@slaves.command("list", short_help="List all WHDLoad Slaves.")
@click.option("-s", "--sort-by",
              type=click.Choice(["id", "date", "dir", "file", "name"]),
              help="Sort the list of WHDLoad Slaves.")
@click.pass_context
def slaves_list(ctx, sort_by):
    """Display a list of all WHDLoad Slaves in the iGameLister WHDLoad Slave data file (slaves.dat).

    The list of WHDLoad Slaves can be sorted by the following criteria:

    \b
      id: The ID number of the WHDLoad Slaves. (default)
    date: The file date of the WHDLoad Slaves.
     dir: The installed directory of the WHDLoad Slaves.
    file: The file name of the WHDLoad Slaves.
    name: The internal name of the WHDLoad Slaves.
    """
    data = Slaves(ctx)
    data.load()
    try:
        data.cli_slaves_list(sort_by)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")


@slaves.command("remove", short_help="Remove a WHDLoad slave.")
@click.argument("slave_id", type=int)
@click.pass_context
def slaves_remove(ctx, slave_id):
    """Remove a WHDLoad Slave from the iGameLister WHDLoad Slave data file (slaves.dat) that has an ID matching SLAVE_ID.
    """
    data = Slaves(ctx)
    data.load()
    try:
        data.cli_slaves_remove(slave_id)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")
    finally:
        data.save()


#
# Slaves Add commands
#


@slaves_add.command("slave", short_help="Add a WHDLoad Slave file.")
@click.argument("source_file", type=click.File("rb"))
@click.argument("installed-path")
@click.pass_context
def slaves_add_slave(ctx, slave_file, installed_path):
    """Add information from a WHDLoad Slave SOURCE_FILE to the iGameLister WHDLoad Slave data file (slaves.dat),
    and set the installed WHDLoad Package location to INSTALLED_PATH.

    \b
    Example
    -------

    You have a WHDLoad Slave file 'AwesomeGame.slave' in the current local directory, and the WHDLoad Package for this
    slave is installed on your Amiga in the path 'DH1:Games/A/AwesomeGame'.

    \b
    igamelister slaves add slave ./AwesomeGame.Slave DH1:Games/A/AwesomeGame
    """
    data = Slaves(ctx)
    data.load()
    try:
        data.cli_slaves_add_slave(slave_file, installed_path)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")
    finally:
        data.save()


@slaves_add.command("archive", short_help="Add all WHDLoad Slaves from a LHA archive file.")
@click.argument("archive_file", type=click.File("rb"))
@click.argument("installed-path")
@click.pass_context
def slaves_add_archive(ctx, archive_file, installed_path):
    """Add information from all WHDLoad Slaves in ARCHIVE_FILE to the iGameLister WHDLoad Slave data file (slaves.dat),
    and set the installed WHDLoad Package location to INSTALLED_PATH.

    \b
    Example
    -------

    You have an archive file 'AwesomeGame.lha' in the current local directory
    with a slave in the archived directory 'AwesomeGame/AwesomeGame.slave',
    and the WHDLoad Package from this archive is installed on your Amiga in
    the path 'DH1:Games/A/AwesomeGame'.

    \b
    igamelister slaves add archive ./AwesomeGame.lha DH1:Games/A
    """
    data = Slaves(ctx)
    data.load()
    try:
        data.cli_slaves_add_archive(archive_file, installed_path)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")
    finally:
        data.save()


@slaves_add.command("path", short_help="Add all WHDLoad Slaves in the path.")
@click.argument("files-path", type=click.Path(exists=True))
@click.argument("installed-path")
@click.option("-r", "--recursive", is_flag=True, help="Recursively scan the path.")
@click.pass_context
def slaves_add_path(ctx, files_path, installed_path, recursive):
    """Add all WHDLoad Slaves from Slave and LHA archive files in FILES_PATH to the iGameLister WHDLoad Slave data file
    (slaves.dat), and set the installed WHDLoad Package location to INSTALLED_PATH.

    \b
    Example
    -------

    You have a collection of slaves and/or archives in the directory and sub-
    directories of './Games', and all of the WHDLoad Packages for these
    files are installed on your Amiga in the path 'DH1:WHDLoad/Games'.

    \b
    igamelister slaves add path -r ./Games DH1:WHDLoad/Games
    """
    data = Slaves(ctx)
    data.load()
    try:
        data.cli_slaves_add_path(files_path, installed_path, recursive)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")
    finally:
        data.save()


#
# Packages commands
#


@packages.group("add")
def packages_add():
    """Add WHDLoad Packages.
    """
    pass


@packages.command("list", short_help="List all WHDLoad Packages.")
@click.option("-s", "--sort-by",
              type=click.Choice(["id", "date", "name"]),
              help="Sort the list of WHDLoad Packages.")
@click.pass_context
def packages_list(ctx, sort_by):
    """Display a list of all WHDLoad Packages in the iGameLister WHDLoad Package data file (packages.dat).

    The list of WHDLoad Packages can be sorted by the following criteria:

    \b
      id: The ID number of the WHDLoad Packages. (default)
    date: The release date of the WHDLoad Packages.
    name: The internal name of the WHDLoad Slaves.
    """
    data = Packages(ctx)
    data.load()
    try:
        data.cli_packages_list(sort_by)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")


@packages.command("find", short_help="Find WHDLoad Packages.")
@click.argument("filter-text")
@click.option("-s", "--sort-by",
              type=click.Choice(["id", "date", "name"]),
              help="Sort the list of WHDLoad Packages.")
@click.pass_context
def packages_find(ctx, filter_text, sort_by):
    """Display a list of all WHDLoad Packages in the iGameLister WHDLoad Package data file (packages.dat) that include
    FILTER_TEXT in the name.

    The list of WHDLoad Packages can be sorted by the following criteria:

    \b
      id: The ID number of the WHDLoad Packages. (default)
    date: The release date of the WHDLoad Packages.
    name: The internal name of the WHDLoad Slaves.
    """
    data = Packages(ctx)
    data.load()
    try:
        data.cli_packages_find(filter_text, sort_by)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")


@packages.command("details", short_help="Show info for a WHDLoad Package.")
@click.argument("package-id", type=int)
@click.pass_context
def packages_details(ctx, package_id):
    """Show the details for a single WHDLoad Package with an ID matching PACKAGE_ID.
    """
    data = Packages(ctx)
    data.load()
    try:
        data.cli_packages_details(package_id)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")


@packages.command("remove", short_help="Remove a WHDLoad package.")
@click.argument("package-id", type=int)
@click.pass_context
def packages_list(ctx, package_id):
    """Remove a single WHDLoad Package from the iGameLister WHDLoad Package data file (packages.dat) that has an
    ID matching PACKAGE_ID.
    """
    data = Packages(ctx)
    data.load()
    try:
        data.cli_packages_remove(package_id)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")
    finally:
        data.save()


#
# Packages Add commands
#


@packages_add.command("all", short_help="Add all WHDLoad Packages.")
@click.pass_context
def packages_add_all(ctx):
    """Add all WHDLoad Packages from every category on the WHDLoad website.
    """
    data = Packages(ctx)
    data.load()
    try:
        data.cli_packages_add_all()
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")
    finally:
        data.save()


@packages_add.command("category", short_help="Add WHDLoad Packages from a category.")
@click.argument("category_type", type=click.Choice(["apps", "cracktros", "demos", "games", "magazines"]))
@click.pass_context
def packages_add_all(ctx, category_type):
    """Add all WHDLoad Packages from CATEGORY_TYPE on the WHDLoad website.

    Valid category types are: apps, cracktros, demos, games, magazines.
    """
    data = Packages(ctx)
    data.load()
    try:
        data.cli_packages_add_category(category_type)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")
    finally:
        data.save()


@packages_add.command("package", short_help="Add a WHDLoad Package.")
@click.argument("page-url")
@click.pass_context
def packages_add_package(ctx, page_url):
    """Add information from a WHDLoad Package at PAGE_URL to the iGameLister WHDLoad Package data file (packages.dat).

    \b
    Example
    -------

    The PAGE_URL argument must be a valid URL for a WHDLoad Package info page on the WHDLoad website
    (http://www.whdload.de/).

    \b
    igamelister packages add package http://www.whdload.de/games/AwesomeGame.html
    """
    data = Packages(ctx)
    data.load()
    try:
        data.cli_packages_add_package(page_url)
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")
    finally:
        data.save()


#
# iGame commands
#


@igame.command("gameslist", short_help="Create gameslist file.")
@click.pass_context
def packages_list(ctx):
    """Create an iGame gameslist file from all WHDLoad Slave and Package details.
    """
    data = Igame(ctx)
    data.load()
    try:
        data.cli_igame_gameslist()
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")


@igame.command("genres", short_help="Create genres file.")
@click.pass_context
def packages_list(ctx):
    """Create an iGame genres file from all WHDLoad Slave and Package details.
    """
    data = Igame(ctx)
    data.load()
    try:
        data.cli_igame_genres()
    except KeyboardInterrupt:
        click.echo("\nInterrupted.")


if __name__ == "__main__":
        cli(sys.argv[1:])
