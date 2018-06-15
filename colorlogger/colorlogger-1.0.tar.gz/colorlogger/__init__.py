import logging
import os
from datetime import datetime
import sys
import atexit
import zipfile

from colorlog import ColoredFormatter


def zipdir(path : str, ziph : zipfile.ZipFile):
    """This function zips a directory

    :param str path: The path
    :param zipfile.ZipFile ziph: The zipfile
    :return: None
    :rtype: None
    """
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def setup(log_level=logging.INFO, filelog=True):
    name = sys.argv[0].split('/')[-1].split('.')[0]
    log_format = "[%(log_color)s%(asctime)s%(reset)s] {%(log_color)s%(pathname)s:%(lineno)d%(reset)s} " \
                 "| " \
                 "%(log_color)s%(levelname)s%(reset)s : %(log_color)s%(" \
                 "message)s%(reset)s"
    file_format = "[%(asctime)s] {%(pathname)s:%(lineno)d}|%(levelname)s : %(message)s"
    formatter = ColoredFormatter(log_format)
    stream = logging.StreamHandler()
    stream.setLevel(log_level)
    stream.setFormatter(formatter)
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(stream)

    if filelog:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        _logdir, logdir = ('logs/' + name,) * 2
        if os.path.exists(logdir):
            num = 1
            while os.path.exists(logdir):
                logdir = _logdir + str(num)
                num += 1
        os.mkdir(logdir)

        for option in ['debug', 'info', 'warning', 'error', 'critical']:
            fh = logging.FileHandler(filename=logdir + '/' + option + '.log')
            fh.setLevel(eval('logging.' + option.upper()))
            fh.setFormatter(logging.Formatter(fmt=file_format))
            log.addHandler(fh)

    def compress_latest():
        zip = zipfile.ZipFile('logs/latest.zip', 'w')
        zipdir(logdir, zip)

    atexit.register(compress_latest)
    return log


def _check(value1, value2):
    if value1 == value2:
        return True
    else:
        return False


def subprocess_info(logger, type_of_log):
    assert type(logger) == logging.Logger, "Logger is not a logger object."
    assert type(type_of_log) == str, "Type_of_log is not a string."
    opt = type_of_log.lower()
    if _check(opt, 'debug'):
        return logger.debug
    elif _check(opt, 'info'):
        return logger.info
    elif _check(opt, 'warn') or _check(opt, 'warning'):
        return logger.warning
    elif _check(opt, 'error') or _check(opt, 'err'):
        return logger.error
    elif _check(opt, 'crit') or _check(opt, 'critical'):
        return logger.critical
    elif _check(opt, 'exception'):
        return logger.exception
    else:
        raise ValueError('Invalid value entered. Enter: debug, info, warn, warning, error, err, crit, critical, '
                         'or exception. Only one can be used at a time.')


def proc_subprocess_logger(process, type_of_log, before='', after=''):
    _logger = type_of_log
    if before:
        _logger(before)
    with process.stdout as output:
        for line in iter(output.readline, b''):
            _logger(line)
    if after:
        _logger(after)


def subprocess_logger(subprocess_cmd, type_of_log, before='', after=''):
    import subprocess
    sub = subprocess.Popen(subprocess_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
    proc_subprocess_logger(sub, type_of_log, before=before, after=after)


def init_func(funcname, logger):
    logger.debug('Starting function definition for ' + funcname + '.')


def function_debug(logger):
    def _function_debug(func):
        def decorator():
            global last_func, val
            exc_exit = False
            noprint = False
            fname = func.__name__
            logger.debug('Starting function %s' % fname)
            start = datetime.now()
            try:
                try:
                    last_func
                except NameError:
                    last_func = {'name': fname, 'runs': 0}
                if fname == last_func['name']:
                    last_func['runs'] += 1
                else:
                    last_func = {'name': fname, 'runs': 0}
                if last_func['runs'] > 250:
                    logger.warning(
                        'Function ' + fname + ' has looped 250 times in a row, RecursonError likely. Exiting...')
                    exc_exit = True
                    sys.exit(1)
                func()
            except Exception:
                logger.exception('An error in the code has occured')
                exc_exit = True
                val = 1
            except (KeyboardInterrupt):
                logger.error('User quit the program')
                exc_exit = True
                val = 0
            except (SystemExit):
                noprint = True
                sys.exit()
            finally:
                if noprint:
                    sys.exit()
                else:
                    finish = datetime.now()
                    diff = finish - start
                    total = str(diff)
                    logger.debug('Finished running func ' + fname + ' in ' + total)
                    if exc_exit:
                        sys.exit(val)

        return decorator

    return _function_debug
