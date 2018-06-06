"""maintenance of mercurial repository sets made easy

The full documentation is available online at https://bitbucket.org/auc/confman
or in the REAMDE.md file.
"""
testedwith = '3.2 3.3 3.4 3.5 3.6 3.7 3.8 3.9 4.0 4.1 4.2 4.3 4.6'

import os.path as osp
from mercurial import extensions

from meta import colortable

from commands import *


def extsetup(ui):
    """ add confman support to hgview """
    try:
        extensions.find('hgview')
    except KeyError:
        return
    try:
        from hgviewlib.util import SUBREPO_GETTERS
    except ImportError:
        return
    def _get_confman(repo_path):
        """ return mapping of section -> path
        for all managed repositories """
        confpath = osp.join(repo_path, '.hgconf')
        if not osp.exists(confpath):
            return None
        from configuration import configurationmanager
        confman = configurationmanager(ui, repo_path, (), {})
        return ((section, conf.get('layout'))
                for section, conf, managed in confman.iterrepos()
                if (managed is not None or
                    conf.get('expand', None) is not None))
    SUBREPO_GETTERS.append(_get_confman)



