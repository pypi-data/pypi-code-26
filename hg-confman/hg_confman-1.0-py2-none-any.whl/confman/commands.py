"This module contains main command actions"
import os
import os.path as osp
import zipfile
from itertools import product

from mercurial import error, archival, scmutil, cmdutil, util
from mercurial.i18n import _

from utils import readconf
from managed import hgrepo, gitrepo
from opts import DEFAULTOPTS, REMOTEOPTS, INCLUDEOPT, EXCLUDEOPT, PULLURIOPT

cmdtable = {}

try:
    # from hg 4.3
    from mercurial import registrar
    command = registrar.command(cmdtable)
except ImportError:
    command = cmdutil.command(cmdtable)


@command('cfensureconf|ensureconf',
         DEFAULTOPTS + REMOTEOPTS + [
             ('s', 'share-path', '', 'specify share path'),
             ('', 'keep-descendant', False,
              'do not update managed if it is on a descendant of track')])
def ensureconf(ui, repo, *args, **opts):
    """update managed repositories using their track value

    It will clone or pull the repositories if needed.

    It updates the repositories to their changeset id in the `.hgsnap`
    file (if it exists) or to the `track` value of the `.hgconf` file
    (if it exists) or to the default branch. It will refuse to operate
    on a repository with uncommitted state.

    If bad changeset id, tag or branch name have been recorded (this
    can happen for the `track` as it is manually handled, and also
    `.hgsnap` can record draft changesets which may be unheard of, or
    even published but not yet pushed changesets), the command will
    complain and proceed to the next.

    """
    confman, repo = readconf(ui, repo, args, opts)
    confman.fill_missing()

    snaps = confman.readsnapshot()

    failedrepos = []
    for section, secconf, managed in confman.iterrepos():
        layout = secconf['layout']
        ui.write(section + '\n', label='confman.section')
        snapshot = snaps.get(layout)
        wctx = managed.workingctx()
        if wctx.hex == snapshot:
            continue # already up to date
        if managed.check_dirty(section):
            failedrepos.append(section)
            continue
        track = secconf.get('track')
        rev = snapshot or track or 'default'
        if managed.revsingle(rev, skiperror=True) == wctx:
            if wctx.branch != track:
                # branch tracks must always be pulled
                continue
        if opts.get('keep_descendant') and managed.is_on_descendant(rev):
            continue
        if not managed.update_or_pull_and_update(section, secconf, rev):
            failedrepos.append(section)

    if failedrepos:
        return 1

# baseline

@command('cfbaseline|baseline',
         DEFAULTOPTS + [
             ('', 'force-hgconf', False, 'force the generation of an .hgconf file'),
             ('', 'propagate', False, 'edit inner configuration also')])
def baseline(ui, repo, *args, **opts):
    """update the track attributes with cset hashes or matching tags

    Maintenance of the baseline is the main purpose of the confman
    extension. This command helps automating its definition.

    If all the managed repositories are aligned on a tag, their
    track attribute will be updated with the shortest tag.

    If some repositories are not tag-aligned, the list of non-aligned
    tags is merely shown.

    The `tip` pseudo-tag is never considered.

    """
    confman, repo = readconf(ui, repo, args, opts)

    tagmap = {}
    untagged = []
    for section, conf, managed in confman.iterrepos():
        track = conf.get('track')
        # we don't record these
        if opts.get('propagate') and 'expand' in conf:
            if not opts.get('root_path'):
                opts['root_path'] = confman.rootpath
            baseline(ui, managed.repo, *args, **opts)
        if track is None and not opts.get('force_hgconf'):
            continue

        ctx = managed.workingctx()
        if ctx.tag:
            if track != ctx.tag:
                tagmap[section] = ctx.tag
        else:
            untagged.append(section)
            if ctx.branch == track:
                continue
            if not managed.unknown_rev(track) and managed.revsingle(track) == ctx:
                continue
            tagmap[section] = ctx.hex

    if untagged:
        ui.write('The following repositories are not tag/branch aligned:\n')
        for section in untagged:
            ui.write('%s\n' % section, label='confman.dirty')
    if not tagmap:
        ui.write('Nothing to do.\n')
        return

    hgconfpath = osp.join(confman.rootpath, '.hgconf')
    if opts.get('force_hgconf'):
        confman.save(hgconfpath)
        ui.write('\nA fresh ".hgconf" has been created\n')
        confman, repo = readconf(ui, repo, args, opts)

    rewritten = confman.save_gently(tagmap)
    if rewritten:
        ui.write('The following entries have been updated:\n')
        for section, tag in rewritten:
            ui.write('%s : ' % section, label='confman.section')
            ui.write('%s\n' % tag, label='confman.tagaligned')



# pull

@command('cfpull', DEFAULTOPTS + REMOTEOPTS)
def pull(ui, repo, *args, **opts):
    """pull managed repositories """
    confman, repo = readconf(ui, repo, args, opts)

    for section, conf, managed in confman.iterrepos():
        ui.write(section + '\n', label='confman.section')
        ui.status('pulling repo %s\n' % section)
        try:
            managed.pull_repo(section, conf)
        except error.RepoError:
            ui.write('unable to pull from ', label='confman.dirty')
            ui.write(conf['pulluri'])
            ui.write('\n')
            continue


# push

@command('cfpush', DEFAULTOPTS + REMOTEOPTS)
def push(ui, repo, *args, **opts):
    """push managed repositories up to their tracked rev """
    confman, repo = readconf(ui, repo, args, opts)

    for section, conf, managed in confman.iterrepos():
        track = conf.get('track')
        if track is None:
            continue
        managed.push_repo(section, conf)

# summary

@command('cfsummary', DEFAULTOPTS)
def summary(ui, repo, *args, **opts):
    """print a summary of the managed repositories

    It presents a description of the state of managed repositories in
    the following format::

      section (branch status phase) [tag] <aligned with baseline> <status>
    """
    confman, repo = readconf(ui, repo, args, opts)
    snaps = confman.readsnapshot()

    def obs(ctx):
        return ' obsolete' if ctx.obsolete() else ''

    def summary(managed, conf, rctx):
        """write an advanced  summary of managed repo at changeset rctx.
        it helps when there are two parents."""
        branch = rctx.branch
        ui.write('(%s' % branch)

        if rctx.obsolete():
            ui.write(' obsolete')

        phase = rctx.phase
        if phase:
           ui.write(' ')
        ui.write('%s' % phase, label='confman.%s-phase' % phase)
        ui.write(') ')

        tags = rctx.tags

        if tags:
            ui.write(min(tags, key=len), ' ')

        if snaps:
            snapshot = snaps.get(conf.get('layout'))
            showsnapshotstate(managed, ui, snapshot, rctx)

        ui.write(' ')

        # baseline state
        track = conf.get('track')
        trackctx = managed.revsingle(track, skiperror=True)
        if track is None:
            ui.write('[no baseline]',
                     label='confman.nobaseline')
        elif track == branch:
            ui.write('[baseline aligned with branch]',
                     label='confman.branchaligned')
        elif track in tags:
            ui.write(u'\N{CHECK MARK}'.encode(ui.fout.encoding
                                              or 'ascii', 'confman'),
                          label='confman.tagaligned')
        elif track == str(rctx.revnum) or rctx.hex.startswith(track):
            ui.write('[baseline aligned with%s cset %s]' % (obs(trackctx), track[:12]),
                     label='confman.csetaligned')
        elif trackctx == rctx:
            ui.write('[baseline aligned with revset %r]' % track,
                     label='confman.revsetaligned')
        elif trackctx in rctx.ancestors():
            ui.write('[at descendant of%s %r]' % (obs(trackctx), track),
                     label='confman.snapolder')
        elif trackctx in rctx.descendants():
            ui.write('[at parent of%s %r]' % (obs(trackctx), track),
                     label='confman.snapnewer')
        elif trackctx:
            ui.write('[baseline%s %r in a parallel branch]' % (obs(trackctx), track),
                     label='confman.snapparallel')
        else:
            ui.write('[baseline says %r]' % track, label='confman.unaligned')

    # show a pseudo-root
    ui.write('%s\n' % osp.basename(confman.rootpath), label='confman.section')
    # start it
    for section, conf, managed in confman.iterrepos():
        node = confman.unicodetreenode(section)
        ui.write(node.encode(ui.fout.encoding or 'ascii', 'treegraph'))
        ui.write(section, label='confman.section')
        if managed.isshared():
            ui.write(' ')
            char = u'\N{MARRIAGE SYMBOL}'.encode(ui.fout.encoding or 'ascii', 'confman')
            ui.write(char, label='confman.shared')
        ui.write(' ')
        rctx = managed.currentctx(allow_p2=True)
        parents = rctx.parents
        nbparents = len(parents)
        if not parents:
            ui.write('\n')
            continue
        for parent in parents:
            if nbparents > 1:
                ui.write('   ')
            summary(managed, conf, parent)
            stat = managed.changestatus()
            if stat and nbparents <= 1:
                ui.write(' ')
                ui.write(stat, label='confman.dirty')
            ui.write('\n')

# archive

@command('cfarchive', DEFAULTOPTS + [
    ('p', 'prefix', '', 'directory prefix for files in archive', 'PREFIX')])
def archive(ui, repo, dest, *args, **opts):
    """create an unversioned zip archive of managed repositories

    Examples:

      hg cfarchive project.zip

    The exact name of the destination archive or directory is given using a
    format string; see "hg help export" for details.

    Each member added to an archive file has a directory prefix prepended. Use
    -p/--prefix to specify a format string for the prefix. The default is the
    basename of the archive, with suffixes removed.

    """
    confman, repo = readconf(ui, repo, args, opts)

    ctx = repo['.']
    dest = cmdutil.makefilename(ctx, dest)
    prefix = archival.tidyprefix(dest, 'zip', opts.get('prefix'))

    # archive confman repo
    matchfn = scmutil.match(ctx, [], opts)
    node = ctx.node()
    archival.archive(repo, dest, node, 'zip',
                     not opts.get('no_decode'), matchfn, prefix)
    # archive managed repos
    snaps = confman.readsnapshot()
    for section, secconf, managed in confman.iterrepos():
        layout = os.path.join(prefix, secconf['layout'])
        ui.write(section + '\n', label='confman.section')
        snapshot = snaps.get(layout)
        track = secconf.get('track')
        rev = snapshot or track or 'default'
        managed.archive(dest, layout, rev)


@command('debugcfarchive', [('X', 'exclude', [], 'patterns to exclude')])
def newarchive(ui, repo, dest, *args, **opts):
    confman, repo = readconf(ui, repo, args, opts)
    arc = zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED)

    def add_files(files, layout):
        ignore = set()
        for pattern, name in product(opts.get('exclude', ()), files):
            if pattern in name:
                ignore.add(name)

        remaining = set(files) - set(ignore)
        for filename in remaining:
            path = osp.join(layout, filename)
            arc.write(path)

    ctx = repo['.']
    node = ctx.node()
    dest = cmdutil.makefilename(ctx, node)
    add_files(ctx.manifest().keys(), '')

    snaps = confman.readsnapshot()
    for section, secconf, managed in confman.iterrepos():

        if managed.check_dirty(section):
            os.remove(dest)
            raise error.Abort(_('cannot archive unclean conf'))

        layout = secconf['layout']
        snapshot = snaps.get(layout)
        track = secconf.get('track')
        rev = snapshot or track or 'default'
        ctx = scmutil.revsingle(managed.repo, rev)
        files = ctx.manifest().keys()
        ui.write('%s (%s) [%s files]' % (section, layout, len(files)) + '\n',
                 label='confman.section')
        add_files(files, layout)

    arc.close()


# broadcast

@command('cfbroadcast|broadcast', DEFAULTOPTS + [
    ('e', 'execute', [], 'execute command')])
def broadcast(ui, repo, *args, **opts):
    """execute a shell command in the context of managed repositories

    The command is any string that can be executed by the default shell of the user.

    The command may contain '%(placeholder)s' that correponds to parameters (ex.
    layout, pulluri) defined in the configuration (.hgconf) section of the active
    managed repository. Aside from these parameters, the '%(section)s'
    placeholder will be replaced by the section name.

    Examples::

      hg broadcast -e "hg paths"
      hg broadcast -e "hg out %(hgrc.paths.review)s"

    """
    confman, repo = readconf(ui, repo, args, opts)

    commands = opts.get('execute')
    if not commands:
        ui.write('nothing to execute\n')
        return

    import subprocess

    for section, conf, managed in confman.iterrepos():
        ui.write('%s\n' % section, label='confman.section')
        params = dict(conf.items() + [('section', section)])
        for command in commands:
            try:
                command = command % params
            except KeyError, err:
                ui.write('skip %s: unknown parameter %s\n' % (section, err),
                         label='confman.dirty')
                continue
            proc = subprocess.Popen(command, shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    cwd=confman.pathfromsection(section))
            out, err = proc.communicate()
            for data in out:
                ui.write(data)


@command('cffiles', DEFAULTOPTS + [
    ('n', 'no-section', False, 'do not display section name'),
    ('0', 'print0', False, 'end filenames with NUL, for use with xargs')])
def files(ui, repo, *args, **opts):
    """list tracked files in the managed repositories

    Print files in the managed repositories in the working directory
    whose names match the given patterns (excluding removed files).

    If no patters are given to match, this command prints the names of
    all files.

    See "hg help files" for more information.
    """
    confman, repo = readconf(ui, repo, args, opts)
    for section, conf, managed in confman.iterrepos():
        if not opts.get('no_section'):
            ui.write(section + '\n', label='confman.section')
        for path in managed.files(opts):
            ui.write(path)


# rewrite repo conf

@command('cfupdateconf', DEFAULTOPTS + [
    ('', 'difftool', 'diff', 'diff command'),
    ('a', 'apply', False, 'really apply the changes (irreversible)')])
def updateconf(ui, repo, *args, **opts):
    """update your managed repos `.hg/hgrc` files with values of the `.hgconf` entries

    For instance, if you added an `hgrc.path.default-push = ...` entry
    to a bunch of repositories, running:

        auc@trantor:~/confs/ariane$ hg cfupdateconf

    will show the proposed changes to the impacted configuration files, in the form of a diff.
    To really apply the changes, just do:

       auc@trantor:~/confs/ariane$ hg cfupdateconf --apply
    """
    confman, repo = readconf(ui, repo, args, opts)

    rewrites = {}
    for section, conf, managed in confman.iterrepos():
        ui.write('%s\n' % section, label='confman.section')
        writtendiff = managed.rewrite_conf(conf)
        if writtendiff:
            ui.write(' ... updated\n')


# requirements.txt handling

@command('debugcfrequirements', [
    INCLUDEOPT, EXCLUDEOPT, PULLURIOPT,
    ('e', 'editable', False, 'use local project path or and develop mode')])
def requirements(ui, repo, *args, **opts):
    """generate a requirements.txt file from the .hgconf specification
    """
    confman, repo = readconf(ui, repo, args, opts)

    with open('requirements.txt', 'wb') as req:
        for section, conf, managed in confman.iterrepos():
            if opts.get('editable'):
                req.write('-e %s\n' % (conf['layout'],))
            else:
                # base case: exists on pypi
                if isinstance(managed, hgrepo):
                    prefix, suffix = 'hg+', '@' + conf.get('track', 'default')
                elif isinstance(managed, gitrepo):
                    prefix, suffix = 'git+', '@' + conf.get('track', 'default')
                else:
                    prefix, suffix = '', ''
                uri = conf.get('hgrc.paths.%s' % opts.get('use_hgrc_path')) or conf['pulluri']
                req.write('%s%s%s\n' % (prefix, uri.format(**conf), suffix))


# DEPRECATED

@command('debugsnapshot', DEFAULTOPTS)
def snapshot(ui, repo, *args, **opts):
    """record changeset ids of the managed repositories into the `.hgsnap` file

    Snapshots are a convenience tool for developers on a project. They
    allow to capture managed repository states in the most precise
    way. While the project and its dependencies advance, feature or
    bugfix-wise, these advancement can be recorded and shared at the
    configuration level. It removes the hassle of manually tracking
    the exact dependencies state for co-developers.

    It is up to you to commit, or discard, the changes made to the
    `.hgsnap` file.

    """
    confman, repo = readconf(ui, repo, args, opts)
    confman.fill_missing()
    confman.snapshot()


def showsnapshotstate(self, ui, snapshot, rctx):
    snaprctx = self.revsingle(snapshot, skiperror=True)
    if snapshot is None:
        ui.write('[no snapshot]',
                 label='confman.nosnap')
    elif self.unknown_rev(snapshot):
        ui.write('[unknown snapshot]',
                 label='confman.snapunknown')
    elif rctx == snaprctx:
        ui.write('[snapshot aligned]',
                 label='confman.snapaligned')
    elif snaprctx in rctx.ancestors():
        ui.write('[at descendant of snapshot]',
                 label='confman.snapolder')
    elif snaprctx in rctx.descendants():
        ui.write('[at parent of snapshot]',
                 label='confman.snapnewer')
    else:
        ui.write('[snapshot in parallel branch]',
                 label='confman.snapparallel')


@command('debugwritegrfiles', DEFAULTOPTS + [PULLURIOPT])
def writegrfiles(ui, repo, *args, **opts):
    "write guestrepo files from configuration.."
    confman, repo = readconf(ui, repo, args, opts)
    with open(os.path.join(confman.rootpath, '.hgguestrepo'), 'w') as gr:
        with open(os.path.join(confman.rootpath, '.hggrmapping'), 'w') as mp:
            for section, secconf, managed in confman.iterrepos():
                if 'expand' in secconf:
                    continue
                layout = secconf.get('layout')
                track = secconf.get('track')
                pulluri = secconf.get('pulluri')
                if opts.get('use_hgrc_path'):
                    pulluri = secconf.get('hgrc.paths.' + opts.get('use_hgrc_path'), pulluri)
                try:
                    ctx = managed.revsingle(track)
                    track = ctx.tag or ctx.hex
                except:
                    pass
                gr.write('%s = %s %s\n' % (layout, section, track))
                mp.write('%s = %s\n' % (section, pulluri))
