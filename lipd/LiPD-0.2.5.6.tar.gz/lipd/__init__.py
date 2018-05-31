from lipd.lipd_io import lipd_read, lipd_write
from lipd.timeseries import extract, collapse, mode_ts, translate_expression, get_matches
from lipd.doi_main import doi_main
from lipd.csvs import get_csv_from_metadata
from lipd.excel import excel_main
from lipd.noaa import noaa_prompt, noaa_to_lpd, lpd_to_noaa, noaa_prompt_1
from lipd.dataframes import *
from lipd.directory import get_src_or_dst, list_files, collect_metadata_file
from lipd.loggers import log_benchmark, logit, verboseit
from lipd.misc import path_type, load_fn_matches_ext, rm_values_fields, get_dsn, rm_empty_fields, print_filename, rm_wds_url, rm_od_url
from lipd.validator_api import call_validator_api, display_results, get_validator_format
from lipd.alternates import FILE_TYPE_MAP
from lipd.json_viewer import viewLipd
from lipd.regexes import re_url
from lipd.fetch_doi import update_dois
from lipd.download_lipd import download_from_url, get_download_path

# Load stock modules
import re
from time import clock
import os
import json
import copy
from collections import OrderedDict


# Global
_timeseries_data = {}

# Notes:
# As a general rule, "D" variables refer to a collection of datasets, and "L" refers to a single dataset
# Default parameters for "options" on select functions are: {"debug": False, "verbose": True}
# For convenience, file metadata is stored as shown below. This is used throughout __init__.py
# File Metadata Format:
# _file_meta = [{"full_path": "/path/to/dir/dataset.lpd",
#               "filename_ext": "dataset.lpd",
#               "filename_no_ext": "dataset",
#               "dir": "/path/to/dir"}, {}...],



def readLipd(path="", dsn=None, options=None):
    """
    Read LiPD file(s)
    Accepts:
    None - opens file browse GUI
    Local file
    Local directory
    URL to direct file

    :param str path: Path to file / directory / URL (optional)
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return dict _d: LiPD Metadata
    """
    # By default, warn users that their old LiPD files will be updated to the most recent version
    __disclaimer("update", options)
    # Debug: start benchmark clock
    _start = clock()
    # Populate the LiPD file metadata in global with the new file(s) data
    _file_meta = __read(path, ".lpd", dsn)
    # Use the LiPD file metadata in global to read the file contents into memory
    _d = __read_lipd_contents(_file_meta, options)
    # Debug: stop benchmark clock
    _stop = clock()
    # Debug: log benchmark stats
    logit(options, "benchmark", "info", log_benchmark("readLipd", _start, _stop))
    # Return LiPD metadata
    return _d


def readExcel(path="", options=None):
    """
    Read Excel file(s)
    Accepts:
    None - opens file browse GUI
    Local file
    Local directory

    :param str path: Path to file / directory (optional)
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return dict _d: LiPD Metadata
    """
    # Debug: start benchmark clock
    _start = clock()
    # Organize file metadata
    _file_meta = __read(path, ".xls")
    # Convert the excel file to LiPD metadata
    _d = excel(_file_meta, options)
    # Debug: stop benchmark clock
    _stop = clock()
    # Debug: log benchmark stats
    logit(options, "benchmark", "info", log_benchmark("readExcel", _start, _stop))
    # Return LiPD metadata
    return _d


def readNoaa(path="", wds_url="", lpd_url="", version="",  options=None):
    """
    Read NOAA file(s) and converts them to LiPD files. LiPD files are saved to local disk
    Accepts:
    None - to trigger file browse GUI
    Local file
    Local directory

    | Example: NOAA to LiPD converter - Use readNoaa function
    | 1: D = lipd.readNoaa(path="/Users/username/Desktop",
    |            wds_url="https://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/NAm2kHydro-2017/noaa-templates/data-version-1.0.0",
    |            lpd_url="https://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/NAm2kHydro-2017/data-version-1.0.0",
    |            version="v1-1.0.0")

    :param str path: Path to file / directory (optional)
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return dict _d: LiPD Metadata
    """
    # Debug: start benchmark clock
    _start = clock()
    # Create file metadata in global
    _file_meta = __read(path, ".txt")
    # Run the NOAA conversion. Create the LiPD files on local disk
    noaa({}, path, wds_url, lpd_url, version, 2,_file_meta, options)
    # Use the same given path to read the LiPD files into the workspace
    _d = readLipd(path)
    # Debug: stop benchmark clock
    _stop = clock()
    # Debug: log benchmark stats
    logit(options, "benchmark", "info", log_benchmark("readNoaa", _start, _stop))
    # Return LiPD metadata
    return _d


def excel(file_meta, options=None):
    """
    Convert Excel files to LiPD files.
    This function saves the LiPD files to disk, and returns the LiPD data in memory

    | Example
    | 1: lipd.readExcel()
    | 2: D = lipd.excel()

    :param list file_meta: Metadata and path info about files being processed
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return dict _d: Metadata
    """
    # Variable for storing LiPD data
    _d = {}
    # Find excel files
    # print("Found " + str(len(file_meta)) + " Excel files")
    # Debug: Note how many files were found
    logit(options, "init", "info", "found excel files: {}".format(len(file_meta)))
    # Debug: start benchmark clock
    _start = clock()
    # Loop for each excel file
    for file in file_meta:
        # Convert excel file to LiPD file. Save LiPD file to disk
        dsn = excel_main(file)
        try:
            # Read the new LiPD file
            # Why do these couple roundabout steps? Because readLipd improves the data, calculates fields, and updates.
            _d[dsn] = readLipd(os.path.join(file["dir"], dsn + ".lpd"))
            # Write the modified LiPD file back out again.
            writeLipd(_d[dsn], os.getcwd())
        except Exception as e:
            # Debug: log error to file
            logit(options["debug"], "init", "error", "excel: Unable to read new LiPD file, {}".format(e))
            # Note the error
            print("Error: Unable to read new LiPD file: {}, {}".format(dsn, e))
    # Debug: stop benchmark clock
    _stop = clock()
    # Debug: log benchmark stats
    logit(options, "benchmark", "info", log_benchmark("excel", _start, _stop))
    # Return LiPD metadata
    return _d


def noaa(D="", path="", wds_url="", lpd_url="", version="", mode=1, file_meta=None, options=None):
    """
    Convert between NOAA and LiPD files

    | Example: LiPD to NOAA converter
    | 1: L = lipd.readLipd()
    | 2: lipd.noaa(D=L,
    |            path="/Users/username/Desktop",
    |            wds_url="https://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/NAm2kHydro-2017/noaa-templates/data-version-1.0.0",
    |            lpd_url="https://www1.ncdc.noaa.gov/pub/data/paleo/pages2k/NAm2kHydro-2017/data-version-1.0.0",
    |            version="v1-1.0.0",
    |            mode=1)

    | Example: NOAA to LiPD converter
    |       DO NOT USE. Use lipd.readNoaa() and refer to its documentation.

    :param dict D: Metadata
    :param str path: Path where output files will be written to
    :param str wds_url: WDSPaleoUrl, where NOAA template file will be stored on NOAA's FTP server
    :param str lpd_url: URL where LiPD file will be stored on NOAA's FTP server
    :param str version: Version of the dataset
    :param int mode: Choose a mode, 1 for LiPD to NOAA, or 2 for NOAA to LiPD
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return none:
    """
    # When going from NOAA to LPD, use the global "files" variable.
    # When going from LPD to NOAA, use the data from the LiPD Library.

    # Choose the mode
    # _mode = noaa_prompt()
    # Debug: start benchmark clock
    _start = clock()
    # LiPD mode: Convert LiPD files to NOAA files
    if mode == 1:
        # _project, _version = noaa_prompt_1()
        # Must provide a version and LiPD URL to complete conversion
        if not version or not lpd_url:
            print("Missing parameters: Please try again and provide all parameters.")
            return
        # Must provide LiPD data to complete conversion
        if not D:
            print("Error: LiPD data must be provided for LiPD -> NOAA conversions")
            return
        # All data was provided, continue
        else:
            # Single dataset provided
            if "paleoData" in D:
                # Make a duplicate of the dataset, to not affect the original
                _d = copy.deepcopy(D)
                # Convert the data, write to NOAA file(s) to disk
                # Receive back
                D = lpd_to_noaa(_d, wds_url, lpd_url, version, path)
            # Multiple datasets provided
            else:
                # For each LiPD file in the LiPD Library
                for dsn, dat in D.items():
                    _d = copy.deepcopy(dat)
                    # Process this data through the converter
                    _d = lpd_to_noaa(_d, wds_url, lpd_url, version, path)
                    # Overwrite the data in the LiPD object with our new data.
                    D[dsn] = _d
            # If no wds url is provided, then remove instances from jsonld metadata
            if not wds_url:
                D = rm_wds_url(D)
            # Write LiPD file(s) to disk, since they now contain the new NOAA URL data
            if(path):
                writeLipd(D, path)
            # No path provided. Write file(s) to cwd by default
            else:
                print("Path not provided. Writing to {}".format(os.getcwd()))
                writeLipd(D, os.getcwd())

    # NOAA mode: Convert NOAA files to LiPD files
    elif mode == 2:
        # Pass through the global files list. Use NOAA files directly on disk.
        noaa_to_lpd(file_meta)
    # No mode selected, quit.
    else:
        print("Invalid mode. Must be 1 for LiPD to NOAA, or 2 for NOAA to LiPD")
    # Debug: stop benchmark clock
    _stop = clock()
    # Debug: log benchmark stats
    logit(options, "benchmark", "info", log_benchmark("noaa", _start, _stop))
    return


def doi(path):
    """
    Use the DOI id stored in the LiPD publication data to fetch new information from the DOI.org using their API.
    Merge the results with the existing data. This process will open the LiPD files on your computer, merge the
    publication data, and overwrite the LiPD files with new LiPD files. This will NOT affect LiPD data currently
    loaded into memory.

    | Example
    | 1: lipd.doi("/path/to/dir")

    :param str path:
    :return none:
    """
    _file_meta = __read(path, ".lpd")
    doi_main(_file_meta)
    return

def fetchDoiWithCsv(csv_source, write_file=True):
    """
    Retrieve DOI publication data for a batch list of DOI IDs that are stored in a CSV file. No LiPD files needed.
    This process uses the DOI.org API for data.

    :param str csv_source: The path to the CSV file stored on your computer
    :param bool write_file: Write the results to a JSON file (default) or print the results to the console.
    :return none:
    """
    update_dois(csv_source, write_file)
    return



def validate(D, detailed=True, options=None):
    """
    Use the Validator API for lipd.net to validate all LiPD files in the LiPD Library.
    Display the PASS/FAIL results. Display detailed results if the option is chosen.

    :param dict D: Metadata (single or multiple datasets)
    :param bool detailed: Show or hide the detailed results of each LiPD file. Shows warnings and errors
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return none:
    """
    # Debug: start benchmark clock
    _start = clock()
    print("\n")
    # Fetch new results by calling lipd.net/api/validator (costly, may take a while)
    print("Fetching results from validator at lipd.net/validator... this may take a few moments.\n")
    try:
        results = []
        # Get the validator-formatted data for each dataset.
        if "paleoData" in D:
            _api_data = get_validator_format(D)
            # A list of lists of LiPD-content metadata
            results.append(call_validator_api(D["dataSetName"], _api_data))
        else:
            for dsn, dat in D.items():
                _api_data = get_validator_format(dat)
                # A list of lists of LiPD-content metadata
                results.append(call_validator_api(dsn, _api_data))
        # Show all dataset names, their pass/fail status, and what errors/warnings they had.
        display_results(results, detailed)
    except Exception as e:
        print("Error: validate: {}".format(e))
        logit(options["debug"], "init", "error", "Error: validate: {}".format(e))
    _stop = clock()
    # In debug mode, note how long the function took to run.
    logit(options["debug"], "benchmark", "info", log_benchmark("validate", _start, _stop))
    return



# PUT


# DATA FRAMES


def ensToDf(ensemble):
    """
    Create an ensemble data frame from some given nested numpy arrays

    :param list ensemble: Ensemble data
    :return obj df: Pandas data frame
    """
    df = create_dataframe(ensemble)
    return df


def tsToDf(tso, options=None):
    """
    Create Pandas DataFrame from TimeSeries object.
    Use: Must first extractTs to get a time series. Then pick one item from time series and pass it through

    :param dict tso: Time series entry
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return dict dfs: Pandas data frames
    """
    # Store data frames
    dfs = {}
    try:
        # Get data frames
        dfs = ts_to_df(tso)
    except Exception as e:
        print("Error: Unable to create data frame")
        logit(options["debug"], "init", "error", "ts_to_df: tso malformed: {}".format(e))
    # Return a dictionary of data frames
    return dfs


# ANALYSIS - TIME SERIES


def extractTs(d, whichtables="meas", mode="paleo", options=None):
    """
    Create a time series using LiPD data (uses paleoData by default)

    | Example : (default) paleoData and meas tables
    | 1. D = lipd.readLipd()
    | 2. ts = lipd.extractTs(D)

    | Example : chronData and all tables
    | 1. D = lipd.readLipd()
    | 2. ts = lipd.extractTs(D, "all", "chron")

    :param dict d: Metadata
    :param str whichtables: "all", "summ", "meas", "ens" - The tables that you would like in the timeseries
    :param str mode: "paleo" or "chron" mode
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return list l: Time series
    """
    # instead of storing each raw dataset per time series object, store it once in the global scope.
    # saves memory and time, though unfortunately it requires global space
    global _timeseries_data
    # List for output time series
    _l = []
    # Debug: start benchmark clock
    # Also, use this as an ID stamp on the timeseries, to differentiate multiple time series runs
    _start = clock()
    try:
        if not d:
            print("Error: LiPD data not provided. Pass LiPD data into the function.")
        else:
            print(mode_ts("extract", mode))
            # If data at the top, that means this is one dataset.
            if "paleoData" in d:
                # One dataset: Process directly on file, don't loop
                try:
                    # Get dataset name. Metadata backup in global is sorted by execution time, and dataset name
                    _dsn = get_dsn(d)
                    # Create a new entry in the global time series variable
                    _timeseries_data[_start] = {}
                    # Backup this dataset to the global variable
                    _timeseries_data[_start][_dsn] = d
                    # Use the LiPD data given to start time series extract
                    print("extracting: {}".format(_dsn))
                    # Copy, so we don't affect the original data
                    _v = copy.deepcopy(d)
                    # Start extract...
                    _l = (extract(_v, whichtables, mode, _start))
                except Exception as e:
                    print("Error: Unable to extractTs for dataset: {}: {}".format(_dsn, e))
                    logit(options, "init", "error",
                          "extractTs: Unable to extractTs for dataset: {}: {}".format(_dsn, e))
            # Multiple datasets to process. Data is nested.
            else:
                # Backup the datasets to the global variable
                _timeseries_data[_start] = d
                # Multiple datasets: Loop and append for each file
                for k, v in d.items():
                    try:
                        # Use the LiPD data given to start time series extract
                        print("extracting: {}".format(k))
                        # Copy, so we don't affect the original data
                        _v = copy.deepcopy(v)
                        # Start extract...
                        _l += (extract(_v, whichtables, mode, _start))
                    except Exception as e:
                        print("Error: Unable to extractTs for dataset: {}: {}".format(k, e))
                        logit(options, "init", "error",
                              "extractTs: Unable to extractTs for dataset: {}: {}".format(k, e))
            # Give some friendly feedback
            print("Created time series: {} entries".format(len(_l)))
    except Exception as e:
        print("Error: Unable to extractTs: {}".format(e))
        logit(options, "init", "error", "extractTs: Exception: {}".format(e))
    # Debug: stop benchmark clock
    _stop = clock()
    # Debug: log benchmark stats
    logit(options, "benchmark", "info", log_benchmark("extractTs", _start, _stop))
    # Return time series list
    return _l


def collapseTs(ts=None, options=None):
    """
    Collapse a time series back into LiPD record form.

    | Example
    | 1. D = lipd.readLipd()
    | 2. ts = lipd.extractTs(D)
    | 3. New_D = lipd.collapseTs(ts)

    _timeseries_data is sorted by time_id, and then by dataSetName
    _timeseries_data[10103341]["ODP1098B"] = {data}

    :param list ts: Time series
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return dict _d: Metadata
    """
    # Retrieve the associated raw data according to the "time_id" found in each object. Match it in _timeseries_data
    global _timeseries_data
    # This will hold the new LiPD data
    _d = {}
    # Oops, the user forgot something
    if not ts:
        print("Error: Time series data not provided. Pass time series into the function.")
    # Time series provided
    else:
        # Send time series list through to be collapsed.
        try:
            # Retrieve the backup LiPD metadata using the original time_id
            _raw = _timeseries_data[ts[0]["time_id"]]
            print(mode_ts("collapse", mode="", ts=ts))
            # Collapse the time series, merging the backup data and time series data where necessary
            _d = collapse(ts, _raw)
            # Get rid of all the trash
            _d = rm_empty_fields(_d)
        except Exception as e:
            print("Error: Unable to collapse the time series: {}".format(e))
            logit(options, "init", "error", "collapseTs: unable to collapse the time series: {}".format(e))
    # Return LiPD metadata
    return _d


def filterTs(ts, expression):
    """
    Create a new time series that only contains entries that match the given expression.

    | Example:
    | D = lipd.loadLipd()
    | ts = lipd.extractTs(D)
    | new_ts = filterTs(ts, "archiveType == marine sediment")
    | new_ts = filterTs(ts, "paleoData_variableName == sst")

    :param str expression: Expression
    :param list ts: Time series
    :return list new_ts: Filtered time series that matches the expression
    """
    # Store matching objects
    new_ts = []
    # Use some magic to turn the given string expression into a machine-usable comparative expression.
    expr_lst = translate_expression(expression)
    # Only proceed if the translation resulted in a usable expression.
    if expr_lst:
        # Expression is good, get anything that matches
        new_ts, _idx = get_matches(expr_lst, ts)
    # Return the *objects* of matching items
    return new_ts


def queryTs(ts, expression):
    """
    Find the indices of the time series entries that match the given expression.

    | Example:
    | D = lipd.loadLipd()
    | ts = lipd.extractTs(D)
    | matches = queryTs(ts, "archiveType == marine sediment")
    | matches = queryTs(ts, "geo_meanElev <= 2000")

    :param str expression: Expression
    :param list ts: Time series
    :return list _idx: Indices of entries that match the criteria
    """
    # Store matching index numbers
    _idx = []
    # Use some magic to turn the given string expression into a machine-usable comparative expression.
    expr_lst = translate_expression(expression)
    # Only proceed if the translation resulted in a usable expression.
    if expr_lst:
        # Expression is good, get anything that matches
        new_ts, _idx = get_matches(expr_lst, ts)
    # Return the *Index numbers* of matching items
    return _idx


def viewTs(ts):
    """
    View the contents of ONE time series entry in a nicely formatted print.

    | Example
    | 1. D = lipd.readLipd()
    | 2. ts = lipd.extractTs(D)
    | 3. viewTs(ts[0])

    :param dict ts: One time series entry
    :return none:
    """
    _ts = ts
    if isinstance(ts, list):
        _ts = ts[0]
        print("It looks like you input a full time series. It's best to view one entry at a time.\n"
              "I'll show you the first entry...")
    _tmp_sort = OrderedDict()
    _tmp_sort["ROOT"] = {}
    _tmp_sort["PUBLICATION"] = {}
    _tmp_sort["GEO"] = {}
    _tmp_sort["OTHERS"] = {}
    _tmp_sort["DATA"] = {}

    # Organize the data by section
    for k,v in _ts.items():
        if not any(i == k for i in ["paleoData", "chronData", "mode", "@context"]):
            if k in ["archiveType", "dataSetName", "googleSpreadSheetKey", "metadataMD5", "tagMD5", "googleMetadataWorksheet", "lipdVersion"]:
                _tmp_sort["ROOT"][k] = v
            elif "pub" in k:
                _tmp_sort["PUBLICATION"][k] = v
            elif "geo" in k:
                _tmp_sort["GEO"][k] = v
            elif "paleoData_" in k or "chronData_" in k:
                if isinstance(v, list) and len(v) > 2:
                    _tmp_sort["DATA"][k] = "[{}, {}, {}, ...]".format(v[0], v[1], v[2])
                else:
                    _tmp_sort["DATA"][k] = v
            else:
                if isinstance(v, list) and len(v) > 2:
                    _tmp_sort["OTHERS"][k] = "[{}, {}, {}, ...]".format(v[0], v[1], v[2])
                else:
                    _tmp_sort["OTHERS"][k] = v

    # Start printing the data to console
    for k1, v1 in _tmp_sort.items():
        print("\n{}\n===============".format(k1))
        for k2, v2 in v1.items():
            print("{} : {}".format(k2, v2))

    return


# SHOW


# def showLipds(D=None):
#     """
#     Display the dataset names of a given LiPD data
#
#     | Example
#     | lipd.showLipds(D)
#
#     :param dict D: LiPD data
#     :return none:
#     """
#
#     if not D:
#         print("Error: LiPD data not provided. Pass LiPD data into the function.")
#     else:
#         print(json.dumps(D.keys(), indent=2))
#     return


# def showMetadata(L):
#     """
#     DEPRECATED
#     Display the metadata specified LiPD in pretty print
#
#     | Example
#     | showMetadata(D["Africa-ColdAirCave.Sundqvist.2013"])
#
#     :param dict L: Metadata
#     :return none:
#     """
#     _tmp = rm_values_fields(copy.deepcopy(L))
#     print(json.dumps(_tmp, indent=2))
#     return


def showDfs(L):
    """
    Display the available data frame names in a given data frame collection

    :param dict L: Data frame collection
    :return none:
    """
    if "metadata" in L:
        print("metadata")
    if "paleoData" in L:
        try:
            for k, v in L["paleoData"].items():
                print(k)
        except KeyError:
            pass
        except AttributeError:
            pass
    if "chronData" in L:
        try:
            for k, v in L["chronData"].items():
                print(k)
        except KeyError:
            pass
        except AttributeError:
            pass
    return


# GET

def getLipdNames(D=None):
    """
    Get a list of all LiPD names in the library

    | Example
    | names = lipd.getLipdNames(D)


    :param dict D: LiPD Metadata
    :return list names: Dataset names
    """
    # Store names of LiPD datasets
    _names = []
    try:
        # No data provided
        if not D:
            print("Error: LiPD data not provided. Pass LiPD data into the function.")
        # Data provided
        else:
            # Get keys (names)
            _names = D.keys()
    except AttributeError:
        # D.keys() failed. Wrong data provided.
        print("Error: Wrong data type provided. Provide a dictionary of datasets.")
    # Return names
    return _names


def getMetadata(L):
    """
    Get metadata from a LiPD data in memory

    | Example
    | m = lipd.getMetadata(D["Africa-ColdAirCave.Sundqvist.2013"])

    :param dict L: One LiPD record
    :return dict _l: LiPD Metadata (No integrated table values)
    """
    _l = {}
    try:
        # Create a copy. Do not affect the original data.
        _l = copy.deepcopy(L)
        # Remove values fields
        _l = rm_values_fields(_l)
    except Exception as e:
        # Input likely not formatted correctly, though other problems can occur.
        print("Error: Unable to get data. Please check that input is LiPD data: {}".format(e))
    return _l


def getCsv(L=None, options=None):
    """
    Get CSV from LiPD metadata

    | Example
    | c = lipd.getCsv(D["Africa-ColdAirCave.Sundqvist.2013"])

    :param dict L: One LiPD record
    :return dict d: CSV data
    """
    # Store values data
    _c = {}
    try:
        # Oops, they forgot.
        if not L:
            print("Error: LiPD data not provided. Pass LiPD data into the function.")
        # Data provided
        else:
            # Get the values from the table metadata.
            _j, _c = get_csv_from_metadata(L["dataSetName"], L)
    except KeyError as ke:
        print("Error: Unable to get data. Please check that input is one LiPD dataset: {}".format(ke))
        logit(options,"init", "error", "Error: Unable to get data. Please check that input is one LiPD dataset: {}".format(ke))
    except Exception as e:
        print("Error: Unable to get data. Something went wrong: {}".format(e))
        logit(options,"init", "error", "getCsv: Exception: Unable to process lipd data: {}".format(e))
    # Return the values, organized by filename
    return _c


# WRITE

def writeLipd(D, path="", options=None):
    """
    Write LiPD data to file(s)

    :param dict D: Metadata
    :param str path: Destination (optional)
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return none:
    """
    # Debug: start benchmark clock
    _start = clock()
    # Write the data to file
    __write_lipd(D, path, options)
    # Debug: stop benchmark clock
    _stop = clock()
    logit(options, "benchmark", "info", log_benchmark("writeLipd", _start, _stop))
    return


# HELPERS


def __universal_read(path, file_type):
    """
    Endpoint for file metadata reading.
    Use a file path to create file metadata and load a file in the appropriate way, according to the provided file type.

    :param str path: Path to file
    :param str file_type: One of approved file types: xls, xlsx, txt, lpd
    :return list files: Sorted file metadata
    """
    # Store list of all file metadata objects
    _file_meta = {}
    # Is this the correct function to load this file type. (i.e. readNoaa for a .txt file)
    correct_ext = load_fn_matches_ext(path, file_type)
    # Does this file path reference a file?
    valid_path = path_type(path, "file")
    # is the path a file?
    if valid_path and correct_ext:
        # get file metadata for one file
        _file_meta = collect_metadata_file(path)
        # Excel and NOAA files need their own print statements. LiPD files have this elsewhere.
        # if file_type in [".xls", ".xlsx"]:
        #     print("reading: {}".format(print_filename(_file_meta["full_path"])))
        # elif file_type == ".txt":
        #     print("reading: {}".format(print_filename(_file_meta["full_path"])))
        # Add the file metadata to the list
        # _files.append(file_meta)
        # we want to move around with the files we load
        # change dir into the dir of the target file
        _cwd = _file_meta["dir"]
        if _cwd:
            os.chdir(_cwd)
    # Return file metadata
    return _file_meta


def __read(path, file_type, dsn=None):
    """
    Determine what path needs to be taken to read in file(s)

    :param str path: Path  (optional)
    :param str file_type: File type to read
    :return none:
    """
    # Store file metadata
    _file_meta = []
    # is there a file path specified ?
    if path:
        # Is this a URL? Download the file and return the local path
        is_url = re.match(re_url, path)
        if is_url:
            # The path will now be a local path to a single file. It will trigger the "elif" statement below
            path = download_from_url(path, get_download_path(), dsn)

        # Directory path
        if os.path.isdir(path):
            _file_meta = __read_directory(path, file_type)
        # File path
        elif os.path.isfile(path):
            _file_meta = __read_file(path, file_type)
        # Invalid path given
        else:
            print("Error: Path given is invalid")

    # no path specified. ask if they want to load dir or file
    else:
        choice = ""
        count = 3
        while not choice:
            try:
                print("Choose a read option:\n1. One file\n2. Multi-file select\n3. Directory")
                choice = input("Option: ")
                print("\n")
                # now use the given file type and prompt answer to call _read_file or _read_dir
                if choice in ["1", "2", "3"]:
                    # open directory picker
                    if choice == "3":
                        # Get file metadata for a directory
                        _file_meta = __read_directory(path, file_type)
                    else:
                        # Get file metdata for single/multi pick
                        _file_meta = __read_file(path, file_type)
                    # A correct choice was made, we can break out of the while loop
                    break
                # Incorrect choice
                else:
                    # Countdown number of failed attempts
                    count -= 1
                if count == 0:
                    print("Error: Too many failed attempts")
                    break
            except Exception as e:
                print("Error: Invalid input: {}".format(e))
    # Return dictionary - file metadata
    return _file_meta


def __read_lipd_contents(file_meta, options):
    """
    Use the file metadata to read in the LiPD file contents as a dataset library

    :param list file_meta: Metadata and path info about files being processed
    :param dict options: Optional settings and modes. (verbose, debug, etc)
    :return dict: Metadata
    """
    # Store LiPD metadata
    _d = {}
    try:
        # Loading one file
        if len(file_meta) == 1:
            # Read in LiPD metadata using the file metadata
            _d = lipd_read(file_meta[0]["full_path"])
            verboseit(options, "Finished read: 1 record")
        # Loading multiple files
        else:
            # Multiple files to read in, loop it
            for file in file_meta:
                # Read in LiPD metadata using the file metadata. Organize by dataset name
                _d[file["filename_no_ext"]] = lipd_read(file["full_path"])
            verboseit(options, "Finished read: {} records".format(len(_d)))
    except Exception as e:
        print("Error: read_lipd_contents: {}".format(e))
        logit(options, "init", "error", "Error: read_lipd_contents: {}".format(e))
    # Return dictionary - LiPD metadata
    return _d


def __read_file(path, file_type):
    """
    Universal read file. Given a path and a type, it will do the appropriate read actions

    :param str path: Path to file
    :param str file_type: One of approved file types: xls, xlsx, txt, lpd
    :return list file_meta: File(s) metadata
    """
    # Store file metadata
    _file_meta = []
    # no path provided. start gui browse
    if not path:
        # src files could be a list of one, or a list of many. depending how many files the user selects. catch all
        src_dir, src_files = get_src_or_dst("read", "file")
        # check if src_files is a list of multiple files
        if src_files:
            for path in src_files:
                _file_meta.append(__universal_read(path, file_type))
        else:
            print("No file(s) chosen")
    else:
         # One file, normal read.
        _file_meta.append(__universal_read(path, file_type))

    # Return list - file metadata
    return _file_meta


def __read_directory(path, file_type):
    """
    Universal read directory. Given a path and a type, it will do the appropriate read actions

    :param str path: Path to directory
    :param str file_type: .xls, .xlsx, .txt, .lpd
    :return list _file_meta: Files Metadata
    """
    _file_meta = []
    # no path provided. start gui browse
    if not path:
        # got dir path
        path, src_files = get_src_or_dst("read", "directory")

    # Check if this is a valid directory path
    valid_path = path_type(path, "directory")

    # If dir path is valid
    if valid_path:
        # List all files of target type in dir
        files_found = []
        # Extra case for xlsx excel files
        if file_type == ".xls":
            files_found += list_files(".xlsx", path)
        files_found += list_files(file_type, path)
        # notify how many files were found
        print("Found: {} {} file(s)".format(len(files_found), FILE_TYPE_MAP[file_type]["file_type"]))
        # Loop for each file found
        for path in files_found:
            # Call read lipd for each file found
            _file_meta.append(__universal_read(path, file_type))
    else:
        print("Directory path is not valid: {}".format(path))
    # Return list - file metadata
    return _file_meta


def __write_lipd(D, path, options):
    """
    Write LiPD data to file, provided an output directory and dataset name.

    :param dict D: Metadata
    :param str path: Destination path
    :param str dsn: Dataset name of one specific file to write
    :return none:
    """
    # no path provided. start gui browse
    if not path:
        # got dir path
        path, _ignore = get_src_or_dst("write", "directory")
    # Check if this is a valid directory path
    valid_path = path_type(path, "directory")
    # If dir path is valid
    if valid_path:
        # Filename is given, write out one file
        if "paleoData" in D:
            try:
                verboseit(options, "writing: {}".format(D["dataSetName"]))
                lipd_write(D, path)
            except KeyError as ke:
                print("Error: Unable to write file: unknown, {}".format(ke))
            except Exception as e:
                print("Error: Unable to write file: {}, {}".format(D["dataSetName"], e))
        # Filename is not given, write out whole library
        else:
            if D:
                for name, lipd_dat in D.items():
                    try:
                        verboseit(options, "writing: {}".format(name))
                        lipd_write(lipd_dat, path)
                    except Exception as e:
                        print("Error: Unable to write file: {}, {}".format(name, e))
                        logit(options, "init", "error", "Error: Unable to write file: {}, {}".format(name, e))

    return


def __disclaimer(mode, options):
    """
    Print the disclaimers once. If they've already been shown, skip over.

    :return none:
    """
    if mode is "update":
        verboseit(options, "Disclaimer: LiPD files may be updated and modified to adhere to standards\n")
    if mode is "validate":
        verboseit(options,
                  "Note: Use lipd.validate() or www.LiPD.net/create to ensure that your new LiPD file(s) are valid")
    return



