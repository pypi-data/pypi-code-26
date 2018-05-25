import os


def should_run(should_old, should_new):
    if not os.path.exists(should_new):
        return(True)

    if os.stat(should_old).st_mtime > os.stat(should_new).st_mtime:
        return(True)

    return(False)


def should_run_olds_new(should_olds, should_new):
    for old in should_olds:
        if should_run(old, should_new):
            return(True)

    return(False)


def should_run_old_news(should_old, should_news):
    for new in should_news:
        if should_run(should_old, new):
            return(True)

    return(False)


def should_run_olds_news(should_olds, should_news):
    for old in should_olds:
        if should_run_old_news(old, should_news):
            return(True)

    return(False)
