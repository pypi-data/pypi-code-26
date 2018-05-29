import re
import sys
import copy
from glob import glob
from os import makedirs
from os.path import splitext, basename, isdir, isfile


class SelectLog:
    def __init__(self, put_log_dir, graph_save_dir, log_date_format):
        self.put_log_dir = put_log_dir
        self.graph_save_dir = graph_save_dir
        self.log_date_format = log_date_format
        self.re_log_date_format =\
            self.log_date_format.replace("YY", "[0-9]{2}") \
                .replace("MM", "[0-2][0-9]") \
                .replace("DD", "[0-3][0-9]") \
                .replace("hh", "[0-2][0-9]") \
                .replace("mm", "[0-5][0-9]") \
                .replace("ss", "[0-5][0-9]")
        self.datetime_len = len(re.sub(r"[^YMDhms]", "", self.log_date_format))
        match = re.search(r"[^YMDhms](?=MM)", self.log_date_format)
        if match:
            self.sep_year_month = match.group(0)
        else:
            self.sep_year_month = ""
        self.date_range = (re.search(r"YY{1,3}", self.log_date_format).span(),
                           re.search(r"MM", self.log_date_format).span(),
                           re.search(r"DD", self.log_date_format).span())

    def get_logfile_paths(self, args):
        if args.input:
            paths = copy.copy(args.input)
        elif args.all:
            paths = self.get_paths_of_all()
        elif args.after:
            paths = self.get_paths_of_after(args.after[0])
        elif args.select:
            paths = self.get_paths_of_select(args.select)
        elif args.new:
            paths = self.get_paths_of_new()
        else:
            print("Error: Please select input log file.")
            sys.exit()

        for path in paths:
            if not isfile(path):
                print(path, "is not exits.")
                paths.remove(path)
        if len(paths) == 0:
            print("There is no target log file.")
            sys.exit()

        return paths

    def setup_save_dir(self, logfile_name):
        if self.is_date_in_fn(logfile_name) is None:
            save_dir = self.graph_save_dir + "other/" + logfile_name
        else:
            date_time, date = self.fn_to_date(logfile_name)
            save_dir = self.graph_save_dir + date + "/" + date_time

        if not isdir(save_dir):
            makedirs(save_dir)
        return save_dir

    def get_paths_of_after(self, date):
        all_paths = self.get_paths_of_all()
        paths = list()
        for path in all_paths:
            fn = self.get_fn(path)
            if self.is_date_in_fn(fn) and\
                    self.fn_to_datetime(fn) >= self.fn_to_datetime(date):
                paths.append(path)
        return paths

    def get_paths_of_new(self):
        paths = list()
        for path in self.get_paths_of_all():
            date_time, date = self.fn_to_date(self.get_fn(path))
            if not isdir(self.graph_save_dir + date + "/" + date_time):
                paths.append(path)
        return paths

    def get_paths_of_select(self, dates):
        paths = list()
        for date in dates:
            path = glob(self.put_log_dir + "**/" + date + ".*", recursive=True)
            if len(path) == 1:
                paths.append(path[0])
            elif len(path) == 0:
                print("Error:", date, "log file is not found")
            else:
                print("Error: found several", date, "log file")
        return paths

    def get_paths_of_all(self):
        return glob(self.put_log_dir + "**/*.*", recursive=True)

    def is_date_in_fn(self, s):
        return re.fullmatch(self.re_log_date_format, s)

    def fn_to_date(self, fn):
        date = fn[self.date_range[0][0]:self.date_range[0][1]] + "" + \
               fn[self.date_range[1][0]:self.date_range[1][1]] + "" + \
               fn[self.date_range[2][0]:self.date_range[2][1]]
        return fn, date

    # filename to date (To remove a non-numeric from a string)
    @staticmethod
    def fn_to_datetime(log_file_name):
        return re.sub(r"[^0-9]", "", log_file_name)

    # file path to filename and remove extension
    @staticmethod
    def get_fn(path):
        return splitext(basename(path))[0]
