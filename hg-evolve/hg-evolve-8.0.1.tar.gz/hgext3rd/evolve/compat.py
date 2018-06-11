# Copyright 2017 Octobus <contact@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""
Compatibility module
"""

import inspect

from mercurial import (
    context,
    mdiff,
    obsolete,
    obsutil,
    repair,
    revset,
    scmutil,
    util,
    vfs as vfsmod,
)
from mercurial.hgweb import hgweb_mod

# hg < 4.6 compat (c8e2d6ed1f9e)
try:
    from mercurial import logcmdutil
    changesetdisplayer = logcmdutil.changesetdisplayer
    changesetprinter = logcmdutil.changesetprinter
    displaygraph = logcmdutil.displaygraph
except (AttributeError, ImportError):
    from mercurial import cmdutil
    changesetdisplayer = cmdutil.show_changeset
    changesetprinter = cmdutil.changeset_printer
    displaygraph = cmdutil.displaygraph

from . import (
    exthelper,
)

eh = exthelper.exthelper()

def isobsnotesupported():
    # hack to know obsnote is supported. The patches for obsnote support was
    # pushed before the obsfateprinter patches, so this will serve as a good
    # check
    if not obsutil:
        return False
    return util.safehasattr(obsutil, 'obsfateprinter')

# Evolution renaming compat

TROUBLES = {}

if not util.safehasattr(context.basectx, 'orphan'):
    TROUBLES['ORPHAN'] = 'unstable'
    context.basectx.orphan = context.basectx.unstable
else:
    TROUBLES['ORPHAN'] = 'orphan'

if not util.safehasattr(context.basectx, 'contentdivergent'):
    TROUBLES['CONTENTDIVERGENT'] = 'divergent'
    context.basectx.contentdivergent = context.basectx.divergent
else:
    TROUBLES['CONTENTDIVERGENT'] = 'content-divergent'

if not util.safehasattr(context.basectx, 'phasedivergent'):
    TROUBLES['PHASEDIVERGENT'] = 'bumped'
    context.basectx.phasedivergent = context.basectx.bumped
else:
    TROUBLES['PHASEDIVERGENT'] = 'phase-divergent'

if not util.safehasattr(context.basectx, 'isunstable'):
    context.basectx.isunstable = context.basectx.troubled

if not util.safehasattr(revset, 'orphan'):
    @eh.revset('orphan')
    def oprhanrevset(*args, **kwargs):
        return revset.unstable(*args, **kwargs)

if not util.safehasattr(revset, 'contentdivergent'):
    @eh.revset('contentdivergent')
    def contentdivergentrevset(*args, **kwargs):
        return revset.divergent(*args, **kwargs)

if not util.safehasattr(revset, 'phasedivergent'):
    @eh.revset('phasedivergent')
    def phasedivergentrevset(*args, **kwargs):
        return revset.bumped(*args, **kwargs)

if not util.safehasattr(context.basectx, 'instabilities'):
    def instabilities(self):
        """return the list of instabilities affecting this changeset.

        Instabilities are returned as strings. possible values are:
         - orphan,
         - phase-divergent,
         - content-divergent.
         """
        instabilities = []
        if self.orphan():
            instabilities.append('orphan')
        if self.phasedivergent():
            instabilities.append('phase-divergent')
        if self.contentdivergent():
            instabilities.append('content-divergent')
        return instabilities

    context.basectx.instabilities = instabilities

# XXX: Better detection of property cache
if 'predecessors' not in dir(obsolete.obsstore):
    @property
    def predecessors(self):
        return self.precursors

    obsolete.obsstore.predecessors = predecessors

if not util.safehasattr(obsolete, '_computeorphanset'):
    obsolete._computeorphanset = obsolete.cachefor('orphan')(obsolete._computeunstableset)

if not util.safehasattr(obsolete, '_computecontentdivergentset'):
    obsolete._computecontentdivergentset = obsolete.cachefor('contentdivergent')(obsolete._computedivergentset)

if not util.safehasattr(obsolete, '_computephasedivergentset'):
    obsolete._computephasedivergentset = obsolete.cachefor('phasedivergent')(obsolete._computebumpedset)

def memfilectx(repo, ctx, fctx, flags, copied, path):
    # XXX Would it be better at the module level?
    varnames = context.memfilectx.__init__.__code__.co_varnames
    ctxmandatory = varnames[2] == "changectx"

    if ctxmandatory:
        mctx = context.memfilectx(repo, ctx, fctx.path(), fctx.data(),
                                  islink='l' in flags,
                                  isexec='x' in flags,
                                  copied=copied.get(path))
    else:
        mctx = context.memfilectx(repo, fctx.path(), fctx.data(),
                                  islink='l' in flags,
                                  isexec='x' in flags,
                                  copied=copied.get(path))
    return mctx

def getcachevfs(repo):
    cachevfs = getattr(repo, 'cachevfs', None)
    if cachevfs is None:
        cachevfs = vfsmod.vfs(repo.vfs.join('cache'))
        cachevfs.createmode = repo.store.createmode
    return cachevfs

def strdiff(a, b, fn1, fn2):
    """ A version of mdiff.unidiff for comparing two strings
    """
    args = [a, '', b, '', fn1, fn2]

    # hg < 4.6 compat 8b6dd3922f70
    argspec = inspect.getargspec(mdiff.unidiff)

    if 'binary' in argspec.args:
        args.append(False)

    return mdiff.unidiff(*args)

# date related

try:
    import mercurial.utils.dateutil
    makedate = mercurial.utils.dateutil.makedate
    parsedate = mercurial.utils.dateutil.parsedate
except ImportError as e:
    import mercurial.util
    makedate = mercurial.util.makedate
    parsedate = mercurial.util.parsedate

def wireprotocommand(exthelper, name, args='', permission='pull'):
    try:
        # Since b4d85bc1
        from mercurial.wireprotov1server import wireprotocommand
        return wireprotocommand(name, args, permission=permission)
    except (ImportError, AttributeError):
        from mercurial import wireproto

    if 3 <= len(wireproto.wireprotocommand.func_defaults):
        return wireproto.wireprotocommand(name, args, permission=permission)

    # <= hg-4.5 permission must be registered in dictionnary
    def decorator(func):
        @eh.extsetup
        def install(ui):
            hgweb_mod.perms[name] = permission
            wireproto.commands[name] = (func, args)
    return decorator

# mercurial <= 4.5 do not have the updateresult object
try:
    from mercurial.merge import updateresult
except (ImportError, AttributeError):
    updateresult = None

# 46c2b19a1263f18a5829a21b7a5053019b0c5a31 in hg moved repair.stripbmrevset to
# scmutil.bookmarkrevs
# This change is a part of 4.7 cycle, so drop this when we drop support for 4.6
try:
    bmrevset = repair.stripbmrevset
except AttributeError:
    bmrevset = scmutil.bookmarkrevs

def hasconflict(upres):
    if updateresult is None:
        return bool(upres[-1])
    return bool(upres.unresolvedcount)
