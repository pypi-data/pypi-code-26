import click

def where(program):
    import os, sys
    
    if sys.platform == "win32" and not program.lower().endswith(".exe"):
        program += ".exe"
    
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program): return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file): return exe_file
    return None

def require_exe(exe):
    if not where(exe):
        click.secho("Cannot find executable '%s'" % exe, fg='red', bold=True, err=True)
        click.exit(1)

def pglob(pattern, recurse=False):
    import fnmatch, glob, os
    matches = []
    if recurse:
        for root, dirnames, filenames in os.walk('.', topdown=False):
            for filename in fnmatch.filter(filenames, pattern):
                m = os.path.join(root, filename)
                if os.path.isfile(m):
                    matches.append(m)
    else:
        for fn in glob.glob(pattern):
            matches.append(fn)
    return matches
