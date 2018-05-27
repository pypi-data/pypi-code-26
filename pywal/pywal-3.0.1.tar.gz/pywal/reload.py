"""
Reload programs.
"""
import logging
import os
import shutil
import subprocess

from .settings import CACHE_DIR, MODULE_DIR, OS
from . import util


def tty(tty_reload):
    """Load colors in tty."""
    tty_script = os.path.join(CACHE_DIR, "colors-tty.sh")
    term = os.environ.get("TERM")

    if tty_reload and term == "linux":
        subprocess.Popen(["sh", tty_script])


def xrdb(xrdb_files=None):
    """Merge the colors into the X db so new terminals use them."""
    xrdb_files = xrdb_files or \
        [os.path.join(CACHE_DIR, "colors.Xresources")]

    if shutil.which("xrdb") and OS != "Darwin":
        for file in xrdb_files:
            subprocess.run(["xrdb", "-merge", "-quiet", file])


def oomox(gen_theme):
    """Call oomox to generate a theme."""
    if gen_theme:
        if not shutil.which("oomox-cli"):
            logging.warning("Oomox not found, skipping.")
            return

        oomox_file = os.path.join(CACHE_DIR, "colors-oomox")

        logging.info("Waiting for Oomox.")
        subprocess.run(["oomox-cli", "-o", "wal", oomox_file],
                       stdout=subprocess.DEVNULL)

    else:
        logging.info("Use -g to generate an oomox theme.")


def gtk():
    """Reload GTK theme on the fly."""
    # Here we call a Python 2 script to reload the GTK themes.
    # This is done because the Python 3 GTK/Gdk libraries don't
    # provide a way of doing this.
    if shutil.which("python2"):
        gtk_reload = os.path.join(MODULE_DIR, "scripts", "gtk_reload.py")
        util.disown(["python2", gtk_reload])

    else:
        logging.warning("GTK2 reload support requires Python 2.")


def i3():
    """Reload i3 colors."""
    if shutil.which("i3-msg"):
        util.disown(["i3-msg", "reload"])


def polybar():
    """Reload polybar colors."""
    if shutil.which("polybar"):
        util.disown(["pkill", "-USR1", "polybar"])


def sway():
    """Reload sway colors."""
    if shutil.which("swaymsg"):
        util.disown(["swaymsg", "reload"])


def colors(cache_dir=CACHE_DIR):
    """Reload colors. (Deprecated)"""
    sequences = os.path.join(cache_dir, "sequences")

    logging.error("'wal -r' is deprecated: "
                  "Use 'cat %s' instead.", sequences)

    if os.path.isfile(sequences):
        print("".join(util.read_file(sequences)), end="")


def env(xrdb_file=None, tty_reload=True):
    """Reload environment."""
    xrdb(xrdb_file)
    i3()
    sway()
    polybar()
    logging.info("Reloaded environment.")
    tty(tty_reload)
