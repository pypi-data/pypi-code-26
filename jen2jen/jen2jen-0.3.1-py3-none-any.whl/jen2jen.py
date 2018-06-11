import logging

from docopt import docopt
from .tools import JenkinsElevator, JenkinsExtractor
from .tiny import Tiny as _h
from .tiny import log_error_and_exit, setup_logger

__version__ = "0.2.0"

logger = logging.getLogger('jen2jen')


def main():
    """
    Usage:
      jen2jen --version
      jen2jen submit [--host <jenkins url>] [--login <username>] [--password <password>] [--local <directory>]
      jen2jen fetch [--host <jenkins url>] [--login <username>] [--password <password>] [--local <directory>]
      jen2jen get-plugins [--host <jenkins url>] [--login <username>] [--password <password>] [--local <directory>]
      jen2jen post-plugins [--host <jenkins url>] [--login <username>] [--password <password>] [--local <directory>]

    Commands:
       fetch              Get the job structure from a remote Jenkins instance and store it locally.
       get-plugins        Get current set of plugins.
       post-plugins       Post current set of plugins.
       submit             Post the jobs from a local directory to some remote Jenkins instance.

    Options:
      -h --help                 Show this screen.
      --host=<hostname>         HTTP-address of a remote Jenkins instance. NB! :8080 may be needed.
      --login=<username>        A remote Jenkins administrator (or equal) account username.
      --password=<password>     A remote Jenkins administrator (or equal) account password.
      --local=<directory>     A remote Jenkins administrator (or equal) account password.
    """
    args = docopt(str(main.__doc__), version=__version__)
    level = getattr(logging, 'DEBUG')
    setup_logger(logger, level)

    if args['fetch']:
        if not args['--host']:
            log_error_and_exit('Please enter Jenkins hostname')
        elif not args['--login']:
            log_error_and_exit('Please enter your username')
        elif not args['--password']:
            log_error_and_exit('Please enter your password')
        elif not args['--local']:
            log_error_and_exit('Please enter local directory path to store the jobs to')
        else:
            jenkins = JenkinsExtractor(
                args['--host'],
                args['--login'],
                args['--password']
            )
            _h.get_to_folder(args['--local'])
            jenkins.extract_jobs()
    if args['submit']:
        if not args['--host']:
            log_error_and_exit('Please enter Jenkins hostname')
        elif not args['--login']:
            log_error_and_exit('Please enter your username')
        elif not args['--password']:
            log_error_and_exit('Please enter your password')
        elif not args['--local']:
            log_error_and_exit('Please enter local directory path to submit the jobs to the remote '
                               'Jenkins instance from')
        else:
            jenkins = JenkinsElevator(
                args['--host'],
                args['--login'],
                args['--password']
            )
            jenkins.process_local_folder(args['--local'])
    if args['get-plugins']:
        if not args['--host']:
            log_error_and_exit('Please enter Jenkins hostname')
        elif not args['--login']:
            log_error_and_exit('Please enter your username')
        elif not args['--password']:
            log_error_and_exit('Please enter your password')
        elif not args['--local']:
            log_error_and_exit('Please enter local directory path to save plugins list to')
        else:
            jenkins = JenkinsExtractor(
                args['--host'],
                args['--login'],
                args['--password']
            )
            jenkins.save_plugins_list(args['--local'])
    if args['post-plugins']:
        if not args['--host']:
            log_error_and_exit('Please enter Jenkins hostname')
        elif not args['--login']:
            log_error_and_exit('Please enter your username')
        elif not args['--password']:
            log_error_and_exit('Please enter your password')
        elif not args['--local']:
            log_error_and_exit('Please enter local directory path to post plugins from')
        else:
            jenkins = JenkinsElevator(
                args['--host'],
                args['--login'],
                args['--password']
            )
            jenkins.install_plugins(args['--local'])
