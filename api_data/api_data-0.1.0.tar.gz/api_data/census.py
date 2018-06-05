# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 12:07:08 2018

@author: Michael Silva
"""
import datetime
import os
import sys
import requests
import asyncio
import pandas as pd
import numpy as np


class api(object):
    """Pull Census API data."""

    def __init__(self, job_id=None, api_key=None, api_key_file=None):
        """Initialize the Census object.

         Parameters
        ----------
        job_id : string, optional
            an identifier of the job
        api_key : string, optional
            Census API key
        api_key_file : string, optional
            The path to a file containing the API key on the first line

        """
        self.api_data = None

        self.api_endpoint = None

        self.api_key = None
        if api_key is not None:
            self.api_key = api_key
        elif api_key_file is not None:
            f = open(api_key_file, 'r')
            self.api_key = f.readline().strip()
            f.close()
        else:
            self.api_key = os.environ.get('CENSUS_API_KEY')

        self.api_variables = None
        self.cache = dict()
        self.debugging = False

        self.df = None
        self.total_steps = 0
        self.current_step = 0

        self.for_strings = {'00': '&for=us:1'}

        if job_id is None:
            job_id = self._now_()
        self.job_id = job_id

        self.log_file = None

        self.root_url = 'https://api.census.gov/data/'

    def _now_(self, include_time=True):
        """Get the current date/time.

         Parameters
        ----------
        include_time : boolean, optional
            True if you want the time included (default).

        Returns
        -------
        now : string
            The current date with/without the time.

        """
        now = datetime.datetime.now()
        if include_time:
            now = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        else:
            now = now.strftime('%Y-%m-%d')
        return now

    def _quit_with_error_(self, error_message):
        self.debug_message(error_message)
        sys.exit(error_message)

    def chunk_variable_list(self, element_list, n=50):
        """Break a list into a list of lists with n elements.

        This is needed because the API has a 50 variable limit.

        Parameters
        ----------
        element_list : list
            a list of elements to be chunked up.
        n : int, optional
            the maximum number of items in the list.

        Returns
        -------
        chunks : list
            a list of lists containing elements in length equal to or under the
            limit.

        """
        chunks = list()
        if len(element_list) < n:
            chunks.append(element_list)
        else:
            j = range((len(element_list) + n - 1) // n)
            chunks = [element_list[i * n:(i + 1) * n] for i in j]
        return chunks

    def create_log_file(self, file_name=None):
        """Create logging text file.

        Parameters
        ----------
        file_name : string, optional
            the name of the log file with the extension.

        """
        if file_name is None:
            now = self._now_(False)
            file_name = 'Census Log ' + now + '.txt'
        f = open(file_name, 'a+')
        f.close()
        self.log_file = file_name
        self.write_to_log_file('Log file created')
        return self

    def debug(self):
        """Enable debug mode."""
        self.debugging = True
        if self.log_file is None:
            self.create_log_file()
        self.write_to_log_file('Debug mode stated')
        return self

    def debug_message(self, message):
        """Write a message to log if debug mode enabled."""
        if self.debugging:
            self.write_to_log_file(message + "(job " + self.job_id + ")")

    def fetch(self, url):
        """Fetch data from a url."""
        self.debug_message('fetch('+url+') called')
        self.current_step = self.current_step + 1
        total_steps = self.total_steps
        self.set_progressbar('Downloading', self.current_step, total_steps)
        return (requests.get(url))

    async def fetch_all(self, urls, ids):
        """Fetch all urls asynchronously."""
        self.debug_message('fetch_all() called')
        self.total_steps = len(urls)
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(None, self.fetch, url) for url in urls]
        i = 0
        for response in await asyncio.gather(*futures):
            response_json = response.json()
            geo_id = ids[i]
            self.cache[response.url] = {'data': response_json.copy(),
                                        'geo_id': geo_id}
            i = i + 1

    def get_data(self, asynchronous=True, quiet_mode=False):
        """Pull data wrapper."""
        self.debug_message('get_data() called')
        if asynchronous:
            return self.get_data_asynchronously(quiet_mode)
        else:
            return self.get_data_synchronously(quiet_mode)

    def get_data_asynchronously(self, quiet_mode=False):
        """Get the data from the API Asynchronously."""
        self.debug_message('aget_data() called')

        # Check if the API parameters are set
        self.validation_check()

        # Chunk up the variable request
        variable_lists = self.chunk_variable_list(self.api_variables)
        # Build url request list
        api_urls = list()
        api_ids = list()
        for geo_id, for_string in self.for_strings.items():
            for variable_list in variable_lists:
                api_url = self.root_url + self.api_endpoint + '?get='
                for census_var in variable_list:
                    api_url += census_var + ','
                api_url = api_url[:-1]
                final_api_url = api_url + for_string + '&key=' + self.api_key
                api_urls.append(final_api_url)
                api_ids.append(geo_id)
        n = str(len(api_urls))
        self.debug_message(n + ' URLS to be pulled asynchronously')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetch_all(api_urls, api_ids))
        loop.close()
        self.debug_message('Event Loop Done')

        self.debug_message('Begining data wrangling')

        current_geo_id = None
        for_df = None
        self.current_step = 0
        self.total_steps = len(self.cache)
        for key, item in self.cache.items():
            self.current_step = self.current_step + 1
            total_steps = self.total_steps
            self.set_progressbar('Processing', self.current_step, total_steps)
            geo_id = item['geo_id']
            response_json = item['data']
            columns = response_json.pop(0)
            chunk_df = pd.DataFrame(response_json, columns=columns)
            replace = {'-666666666': np.NaN, '-222222222': np.NaN}
            chunk_df.replace(replace, inplace=True)
            if geo_id == current_geo_id:
                # Widen the data frame with the additional data
                for_df = pd.concat([for_df, chunk_df.copy()], axis=1)
            else:
                if for_df is not None:
                    # Convert data to numeric
                    for census_var in self.api_variables:
                        for_df[census_var] = for_df[census_var].apply(pd.to_numeric, errors='ignore')
                    # Keep only the variables specified
                    for_df = for_df[self.api_variables]
                    # Add geoid
                    for_df.loc[0, 'geo_id'] = current_geo_id
                    # Save it
                    if self.df is None:
                        self.df = for_df.copy()
                    else:
                        self.df = self.df.append(for_df.copy(), ignore_index=True)
                for_df = chunk_df.copy()
            current_geo_id = geo_id
            if self.current_step == self.total_steps:
                # Append the last record
                for_df.loc[0, 'geo_id'] = current_geo_id
                for_df = for_df[list(self.df.columns.values)]
                self.df = self.df.append(for_df, ignore_index=True)

        if self.df is not None:
            # reset the pandas data frame index
            self.df = self.df.reset_index(drop=True)
        self.debug_message('Data wrangling done')
        return(self.df)

    def get_data_synchronously(self, quiet_mode=False):
        """Get the data from the API."""
        self.debug_message('sget_data() called')

        # Check if the API parameters are set
        self.validation_check()

        # Chunk up the variable request
        variable_lists = self.chunk_variable_list(self.api_variables)

        # Make the requests
        self.total_steps = len(self.for_strings) * len(variable_lists)

        for geo_id, for_string in self.for_strings.items():
            self.write_to_log_file('Getting data for: ' + str(geo_id))
            for_df = None
            for variable_list in variable_lists:
                api_url = self.root_url + self.api_endpoint + '?get='
                for census_var in variable_list:
                    api_url += census_var + ','
                api_url = api_url[:-1]
                final_api_url = api_url + for_string + '&key=' + self.api_key
                response_json = None
                try:
                    # Look for response in the cache
                    if final_api_url in self.cache:
                        self.debug_message('Found data in cache')
                        response_json = self.cache[final_api_url]
                    else:
                        self.debug_message('API call: ' + final_api_url)
                        response = requests.get(final_api_url)
                        # Parse the response
                        response_json = response.json()
                        self.cache[final_api_url] = response_json.copy()
                except:
                    error_message = "ERROR: Failed to pull data from API!"
                    self.debug_message(error_message)
                    if quiet_mode is False:
                        print(error_message + " - " + final_api_url)

                current_step = self.current_step = self.current_step + 1
                total_steps = self.total_steps
                self.set_progressbar('Progress', current_step, total_steps)

                if response_json is None:
                    self.debug_message('response_json not defined')
                else:
                    # Load the data into a data frame
                    columns = response_json.pop(0)
                    chunk_df = pd.DataFrame(response_json, columns=columns)
                    replace = {'-666666666': np.NaN, '-222222222': np.NaN}
                    chunk_df.replace(replace, inplace=True)
                    # Convert the requested data to numeric
                    for census_var in variable_list:
                        chunk_df[census_var] = chunk_df[census_var].apply(pd.to_numeric, errors='ignore')
                    # Create a dataframe or add the new columns to it
                    if for_df is None:
                        for_df = chunk_df.copy()
                    else:
                        for_df = pd.concat([for_df, chunk_df.copy()], axis=1)

            if for_df is not None:
                # Only keep the data you have requested
                for_df = for_df[self.api_variables]
                # Add in the geo id
                for_df.loc[0, 'geo_id'] = str(geo_id)
                # Add to self.df
                if self.df is None:
                    self.df = for_df
                else:
                    self.df = pd.concat([self.df, for_df])

        if self.df is not None:
            # reset the pandas data frame index
            self.df = self.df.reset_index(drop=True)
        return(self.df)

    def set_api_endpoint(self, api_endpoint):
        """Set the API endpoint."""
        self.api_endpoint = api_endpoint
        self.debug_message('API endpoint set to ' + api_endpoint)
        return self

    def set_api_key(self, api_key):
        """Set the API key."""
        self.api_key = api_key
        hidden_api_key = '*' * len(self.api_key)
        self.debug_message('API key set to ' + hidden_api_key)
        return self

    def set_api_variables(self, api_variables):
        """Set the variable to request from the API."""
        self.api_variables = api_variables
        return self

    def set_for_strings(self, for_strings):
        """Set the dictionary of geographies to pull the data for."""
        self.for_strings = for_strings
        self.debug_message('API for strings set to ' + str(for_strings))
        return self

    def set_job_id(self, job_id):
        """Set a unique id for this job."""
        self.job_id = job_id
        self.debug_message('Job id set to ' + job_id)
        return self

    def set_progressbar(self, message, numerator, denominator):
        """Update the progress indicator."""
        percent_complete = int((numerator / denominator) * 100)
        if percent_complete == 100:
            flush = False
            end = '\n'
        else:
            flush = True
            end = ''
        print("\r"+message+": %d%%" % percent_complete, end=end, flush=flush)

    def validation_check(self):
            """Validate Parameters prior to requesting."""
            self.debug_message('validation_check() called')
            # Check if the API parameters are set
            e = 'ERROR: '
            if self.api_key is None:
                self._quit_with_error_(e + 'Census API key not defined')
            if self.api_endpoint is None:
                self._quit_with_error_(e + 'Census API endpoint not defined')
            if self.api_variables is None:
                self._quit_with_error_(e + 'Census API variables not defined')
            self.debug_message('Passed validation')

    def write_to_log_file(self, message):
        """Write a message to the debug text log."""
        if self.log_file is None:
            print("Log file wasn't created")
        else:
            now = self._now_()
            f = open(self.log_file, 'a')
            f.write(now + ' > ' + message + '\n')
            f.close()
        return self
