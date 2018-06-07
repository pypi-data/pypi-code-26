#!/usr/bin/env python3
import site
from pathlib import Path

# Have coherent application icon paths after package deployment for all supported platforms
# XXX: A bit of a hack right now, for sure there are better ways to develop and deploy

# Deployed
site_path = Path(site.getsitepackages()[0])
site_path = site_path.parents[2] / 'share' / 'icons'

# Development
this_script_path = Path(__file__)
ICON_PATH = this_script_path.parents[1] / 'share' / 'icons'

if ICON_PATH.is_dir():
    print("We are in development path mode, icons are in: {}".format(ICON_PATH))
elif site_path.is_dir():
    print("We are in deployed mode, icons are in: {}".format(site_path))
    ICON_PATH = site_path
