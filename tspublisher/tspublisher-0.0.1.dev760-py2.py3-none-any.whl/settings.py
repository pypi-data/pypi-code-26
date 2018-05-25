from __future__ import absolute_import, division, print_function, unicode_literals

import os
import platform

GIT_DIRECTORY = os.path.expanduser("~/git")
PROCEDURE_CHECKOUT_DIRECTORY = os.path.expanduser("~/git/content-procedures")
CHANNELS_CHECKOUT_DIRECTORY = os.path.expanduser("~/git/content-channels")
STUDIO_GIT_PATH = 'studio-git.touchsurgery.com'
PROCEDURE_REPOSITORY = 'studio-git.touchsurgery.com:/srv/git/procedure-repo'
CHANNELS_REPOSITORY = 'studio-git.touchsurgery.com:/srv/git/channel-repo'

SSH_DIRECTORY_PATH = os.path.expanduser('~/.ssh')
SSH_CONFIG_PATH = os.path.expanduser("~/.ssh/config")
RSA_PUBLIC_KEY_PATH = os.path.expanduser('~/.ssh/touchsurgery_publisher_rsa.pub')
RSA_PRIVATE_KEY_PATH = os.path.expanduser('~/.ssh/touchsurgery_publisher_rsa')

if platform.system() == "Windows":
    BASE_DATA_DIR = "Z:\\"
else:
    BASE_DATA_DIR = os.path.join("/Volumes", "content")

PRODUCTION_INFO_DIR = os.path.join(BASE_DATA_DIR, "productionInfo")
PRODUCTION_INFO_BACKUP_DIR = os.path.expanduser("~/git/production-info")
CHANNELS_INFO_DIR = CHANNELS_CHECKOUT_DIRECTORY

CONTENT_DB_DIR = os.path.join(BASE_DATA_DIR, "assetdb", ".db", "contentdb.sqlite3")

ORIGINAL_CONTENT_ROOT = "C:/TouchSurgery/assetdb/vault2"
ORIGINAL_CONTENT_ROOT_OLD = "C:/TouchSurgery/assetdb"
if platform.system() == "Windows":
    REPLACEMENT_CONTENT_ROOT = "C:/TouchSurgery/assetdb/vault2"
    REPLACEMENT_CONTENT_ROOT_OLD = "C:/TouchSurgery/assetdb"
else:
    REPLACEMENT_CONTENT_ROOT = "/Volumes/content/assetdb/vault2"
    REPLACEMENT_CONTENT_ROOT_OLD = "/Volumes/content/assetdb"

CG_APP5_ROOT = os.path.join(BASE_DATA_DIR, "delivery", "app5")
VBS_ROOT = os.path.join(BASE_DATA_DIR, "delivery", "vbs")
VBS_BACKUP_ROOT = PROCEDURE_CHECKOUT_DIRECTORY
