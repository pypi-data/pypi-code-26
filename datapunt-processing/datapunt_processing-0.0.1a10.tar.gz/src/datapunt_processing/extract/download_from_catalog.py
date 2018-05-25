#!/usr/bin/env python

import os
import re
import shutil
import argparse
import pprint
import requests
import urllib.parse as urlparse
from datapunt_processing.helpers.files import create_dir_if_not_exists, unzip


def get_catalog_package_id(url):
    """
    Retrieve dcatd URI from full url from data.amsterdam.nl, for example: dcatd/datasets/inzameldagen-grofvuil-huisvuil

    Args:
        url: full data.amsterdam.nl url of the desired dataset, for example: https://data.amsterdam.nl/#?dte=dcatd%2Fdatasets%2Finzameldagen-grofvuil-huisvuil&dtfs=T&mpb=topografie&mpz=11&mpv=52.3731081:4.8932945

    Result:
       Unique id number of package.
    """
    decoded_url = urlparse.unquote(url)
    parsed_url = urlparse.urlparse(decoded_url)
    print(parsed_url)
    meta_id = urlparse.parse_qs(parsed_url.fragment)['?dte'][0]
    print(meta_id)
    return meta_id


def download_metadata(url):
    """
    Download files from data catalog using the dcatd identifier.

    Args:
        url: full data.amsterdam.nl url of the desired dataset, for example: https://data.amsterdam.nl/#?dte=dcatd%2Fdatasets%2Finzameldagen-grofvuil-huisvuil&dtfs=T&mpb=topografie&mpz=11&mpv=52.3731081:4.8932945

    Result:
       All the Metadata from this dataset as a json dictonary, with the owner, refresh data, resource url's to the desired files, etc.
    """
    package_id = get_catalog_package_id(url)
    METADATA_URL = 'https://api.data.amsterdam.nl/{}'.format(package_id)
    print("Downloading metadata from", METADATA_URL)
    metadata_res = requests.get(METADATA_URL)
    metadata_res.raise_for_status()

    metadata = metadata_res.json()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(metadata)
    return metadata


def download_all_files(metadata, download_directory):
    """
    Download all files from metadata resources list.

    Args:
       1. metadata: json dictonary from ckan with all the metadata including the resources list of all files.
       2. download_directory: path where to store the files from the files, for example data.

    Result:
        Unzipped and created dir filled with all data in the download_directory, if this does not yet exists.
    """
    for result in metadata['dcat:distribution']:
        if (result['dcat:accessURL'] is not None and
        result['ams:distributionType'] == 'file' and
        result['ams:resourceType'] == 'data'):
            create_dir_if_not_exists(download_directory)
            download_file(result['dcat:accessURL'], download_directory)


def download_file(file_location, target):
    print("Downloading File from URI: ", file_location)
    file = requests.get(file_location, stream=True)
    if file.headers['Content-type'] in ('application/json', 'text/html; charset=UTF-8'):
        print('Skipping, probably not a file, probably an api or html page')
    else:
        cd =file.headers.get('Content-Disposition')
        filename = re.findall('filename="(.*)";', cd)[0]
        print(filename)
        full_path = os.path.join(target, filename)
        print(full_path)
        with open(full_path, 'wb') as f:
            file.raw.decode_content = True
            shutil.copyfileobj(file.raw, f)
        print("Downloaded as", full_path)


def parser():
    """Parser function to run arguments from commandline and to add description to sphinx."""
    example_url = 'https://data.amsterdam.nl/#?dte=dcatd%2Fdatasets%2Finzameldagen-grofvuil-huisvuil&dtfs=T&mpb=topografie&mpz=11&mpv=52.3731081:4.8932945'
    parser = argparse.ArgumentParser(
        description="""
        Get data and metadata from data.amsterdam.nl,
        unzip if needed and put the file in a local directory.
        To test run this command line:
        ``download_from_catalog {} data``
        """
        .format(example_url))

    parser.add_argument(
        'url',
        type=str,
        help="""
        Insert full url from main result page of dataset, for example:
        {}
        """.format(example_url))
    parser.add_argument(
        'output_folder',
        type=str,
        help="""
        Specify the desired output folder path, for example: app/data""")
    #parser.add_argument('--f','filename_as_folder', default=False, help='use --f=True to unzip to subfolders with name of zipfile.')
    return parser


def main():
    args = parser().parse_args()
    metadata = download_metadata(args.url)
    download_all_files(metadata, args.output_folder)
    unzip(args.output_folder)


if __name__ == "__main__":
    main()
