"""Create cron schedule from exported data with `crontab -l` ."""

from crontab import CronTab
from datetime import timedelta
from datetime import datetime
import os
import re
import sys
import warnings


# Ignore cases when reading crontab file.
IGNORE_CASES = ['MAILTO', '#']


def stop_future_warning(func):
    """Stop printing warning."""
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', FutureWarning)
            return func(*args, **kwargs)
    return wrapper

def export(targets):
    header = 'date,hour,miniute,second,scrip,server\n'
    with open('result.csv', 'w') as f:
        f.write(header)
        for t, s in targets:
            result = '{0},{1},{2}\n'.format(
                    t.strftime('%Y-%m-%d,%H,%M,%S'),
                    s[1],
                    s[0])
            f.write(result)

def execute_from_console():
    return parse_command()

def parse_command():
    import argparse
    p = argparse.ArgumentParser(description="Download sites.")
    p.add_argument('-s', '--start', type=str,
                   default=datetime.now().strftime('%Y%m%d000000'),
                   help='Cron start datetime.(YYYYmmddHHMMSS)',
                   dest='start_datetime' )
    p.add_argument('-e', '--end', type=str,
                   help='Cron end datetime.(YYYYmmddHHMMSS)',
                   default=datetime.now().strftime('%Y%m%d235959'),
                   dest='end_datetime')
    p.add_argument('-d', '--directory', type=str,
                   help='Directory name excluding cron files.',
                   default='crontab',
                   dest='directory')
    args = p.parse_args()
    start = args.start_datetime
    end = args.end_datetime
    directory = args.directory
    if not has_directory(directory):
        sys.exit(1)
    
    export(Cron(start, end, directory))

def has_directory(directory):
    if os.path.isdir(directory):
        return True
    print("""
You must make `crontab` directory to load crontab files.
If you don't want this name, you can chose your prefere name with argument of
`-d`. Please see help command.\n""")
    return False


class Cron(object):

    def __init__(self, start, end, directory='crontab'):
        start_dt = datetime.strptime(start, '%Y%m%d%H%M%S')
        end_dt = datetime.strptime(end, '%Y%m%d%H%M%S')
        self.crons = self.__quote(directory, start_dt, end_dt)

    @stop_future_warning
    def __quote(self, directory, start, end):
        targets = {}
        for sv, lines in self.create_file_object_by_server(directory).items():
            for li in lines:
                li = li.rstrip()
                if not self.is_cron_script(li):
                    continue

                nz_crnon = self.normalize_cron_script(li)
                cron_time = nz_crnon[0]
                cron_script = nz_crnon[1]

                # TODO: has to handle error occuring missed cron script.
                c = CronTab(cron_time)

                current_time = start
                while current_time <= end:
                    interval_second = c.next(current_time)
                    current_time = current_time + \
                        timedelta(seconds=interval_second)
                    if current_time > end:
                        break
                    cron_combo = (sv, cron_script)
                    if current_time not in targets:
                        targets[current_time] = [cron_combo]
                    else:
                        targets[current_time].append(cron_combo)
        return targets
    
    def __iter__(self):
        for t, scripts in sorted(self.crons.items()):
            for s in scripts:
                yield (t, s)

    def create_file_object_by_server(self, directory):
        """Read cronfile and create file object."""
        server_list = {}
        for server_file in os.listdir(directory):
            file_path = os.path.join(directory, server_file)
            with open(file_path, 'r') as f:
                lines = f.readlines()
                name, __ext = os.path.splitext(server_file)
                server_list[name] = lines
        return server_list

    def is_cron_script(self, cron_script):
        for ic in IGNORE_CASES:
            if ic in cron_script or cron_script == '':
                return False
        return True

    def normalize_cron_script(self, cron_script):
        results = re.split("[ \t]+", cron_script)
        return (' '.join(results[0:5]), results[-1])


if __name__ == '__main__':
    parse_command()
