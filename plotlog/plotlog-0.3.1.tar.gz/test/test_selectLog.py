import unittest

from plotlog.selectlog import SelectLog
import create_exlog as ce


class TestSelectLog(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_paths_of_all(self):
        self.sl = SelectLog("log/", "graph/", "YYMMDDhhmmss")
        ce.create_exlog(log_date_type=0)
        all_paths = [f[1]+f[0][2:]+".csv" for f in ce.default_files]
        get_all_paths = self.sl.get_paths_of_all()

        for all_path in all_paths:
            self.assertIn(all_path, get_all_paths)
        for get_all_path in get_all_paths:
            self.assertIn(get_all_path, all_paths)

    def test_get_paths_of_after(self):
        self.sl = SelectLog("log/", "graph/", "YYMMDDhhmmss")
        ce.create_exlog(log_date_type=0)
        after_date = "170102200000"
        get_after_paths = self.sl.get_paths_of_after(after_date)
        after_paths = [f[1]+f[0][2:]+".csv" for f in ce.default_files if int(f[0][2:]) >= int(after_date)]
        for after_path in after_paths:
            self.assertIn(after_path, get_after_paths)
        for get_after_path in get_after_paths:
            self.assertIn(get_after_path, after_paths)

    def test_get_paths_of_select(self):
        self.sl = SelectLog("log/", "graph/", "YYMMDDhhmmss")
        ce.create_exlog(log_date_type=0)
        sel_dates = ["170102200000", "170102000000"]
        get_sel_paths = self.sl.get_paths_of_select(sel_dates)
        sel_paths = []
        for sel_date in sel_dates:
            for f in ce.default_files:
                if int(f[0][2:]) == int(sel_date):
                    sel_paths.append(f[1] + f[0][2:] + ".csv")

        for sel_path in sel_paths:
            self.assertIn(sel_path, get_sel_paths)
        for get_sel_path in get_sel_paths:
            self.assertIn(get_sel_path, sel_paths)

    def test_get_paths_of_new(self):
        self.sl = SelectLog("log/", "graph/", "YYMMDDhhmmss")
        ce.create_exlog(log_date_type=0)
        if ce.isdir("./graph"):
            ce.rmtree("./graph")
        sel_dates = ["170102200000", "170101120000", "170102180000"]
        get_sel_paths = self.sl.get_paths_of_select(sel_dates)
        for path in get_sel_paths:
            self.sl.setup_save_dir(self.sl.get_fn(path))

        get_new_paths = self.sl.get_paths_of_new()
        new_paths = [f[1]+f[0][2:]+".csv" for f in ce.default_files]
        for get_sel_path in get_sel_paths:
            new_paths.remove(get_sel_path)

        for new_path in new_paths:
            self.assertIn(new_path, get_new_paths)
        for get_new_path in get_new_paths:
            self.assertIn(get_new_path, new_paths)

    def test_filename_to_date(self):
        self.sl = SelectLog("log/", "graph/", "YY-MM-DD_hh-mm-ss")
        log_file_name = "17-01-02 20,00,00.csv"
        log_file_date = self.sl.fn_to_datetime(log_file_name)
        self.assertEqual("170102200000", log_file_date)

    def test_get_paths_of_all_other_type(self):
        self.sl = SelectLog("log/", "graph/", "YY-MM-DD_hh-mm-ss")
        ce.create_exlog(log_date_type=4)
        all_paths = [ce.type_four(f) for f in ce.default_files]
        get_all_paths = self.sl.get_paths_of_all()

        for all_path in all_paths:
            self.assertIn(all_path, get_all_paths)
        for get_all_path in get_all_paths:
            self.assertIn(get_all_path, all_paths)

    def test_is_date_in_fn(self):
        self.sl = SelectLog("log/", "graph/", "YY-MM-DD_hh-mm-ss")
        self.assertTrue(self.sl.is_date_in_fn("17-10-31_01-00-00"))

    def test_get_paths_of_after_other_type(self):
        self.sl = SelectLog("log/", "graph/", "YY-MM-DD_hh-mm-ss")
        ce.create_exlog(log_date_type=4)
        after_date = "17-01-02_20-00-00"
        get_after_paths = self.sl.get_paths_of_after(after_date)
        after_paths = []
        for f in ce.default_files:
            if int(self.sl.fn_to_datetime(f[0][2:])) >= int(self.sl.fn_to_datetime(after_date)):
                after_paths.append(ce.type_four(f))
        for after_path in after_paths:
            self.assertIn(after_path, get_after_paths)
        for get_after_path in get_after_paths:
            self.assertIn(get_after_path, after_paths)

    def test_get_paths_of_select_other_type(self):
        self.sl = SelectLog("log/", "graph/", "YY-MM-DD_hh-mm-ss")
        ce.create_exlog(log_date_type=4)
        sel_dates = ["17-01-02_20-00-00", "17-01-02_00-00-00"]
        get_sel_paths = self.sl.get_paths_of_select(sel_dates)
        sel_paths = []
        for sel_date in sel_dates:
            for f in ce.default_files:
                if int(self.sl.fn_to_datetime(f[0][2:])) == int(self.sl.fn_to_datetime(sel_date)):
                    sel_paths.append(ce.type_four(f))

        for sel_path in sel_paths:
            self.assertIn(sel_path, get_sel_paths)
        for get_sel_path in get_sel_paths:
            self.assertIn(get_sel_path, sel_paths)

    def test_get_paths_of_new_other_type(self):
        self.sl = SelectLog("log/", "graph/", "YY-MM-DD_hh-mm-ss")
        ce.create_exlog(log_date_type=4)
        if ce.isdir("./graph"):
            ce.rmtree("./graph")
        sel_dates = ["17-01-02_20-00-00", "17-01-01_12-00-00", "17-01-02_18-00-00"]
        get_sel_paths = self.sl.get_paths_of_select(sel_dates)
        for path in get_sel_paths:
            self.sl.setup_save_dir(self.sl.get_fn(path))

        get_new_paths = self.sl.get_paths_of_new()
        new_paths = [ce.type_four(f) for f in ce.default_files]
        for get_sel_path in get_sel_paths:
            new_paths.remove(get_sel_path)

        for new_path in new_paths:
            self.assertIn(new_path, get_new_paths)
        for get_new_path in get_new_paths:
            self.assertIn(get_new_path, new_paths)
