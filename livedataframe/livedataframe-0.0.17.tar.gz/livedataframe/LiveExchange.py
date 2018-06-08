import pandas as pd
import json
import requests
import threading
from datetime import datetime, timedelta

import time
from urllib.parse import urlencode
import hashlib
import hmac
import base64
import pkg_resources

from livedataframe.SocketManager import SocketManager

class LiveExchange():
    def __init__(self, exchange, symbols, lookback_period, public_key, secret_key, ip='api.livedataframe.com' , timezone = None):
        self.symbols = {}
        self.exchange = exchange

        self.requested_symbols = symbols
        self.stop_everything = False
        self.lookback_period = lookback_period
        self.public_key = public_key
        self.secret_key = secret_key
        self.ip = ip

        self.socket_manager_identifier = self.exchange + '_SOCKET_MANAGER'

        self.params = {
            "exchange": exchange,
            "symbols": symbols,
            "lookback_period": lookback_period,
            "client_version": pkg_resources.get_distribution("livedataframe").version
            }

        self._validate_params(self.params)

        self.lock = threading.Lock()

        self.errors = []
        self.messages = []

        self.timezone = timezone


    def start(self):

        try:
            self._load_configs_and_messages()

            self._get_active_symbols_if_all_specified()

            self._configure_and_start_socket_manager()

            time_chunks = self._generate_time_chunks(self.lookback_period)
            absolute_start_time = datetime.now()

            self._query_historical_chunks(time_chunks)


            print("TOTAL TIME TO LOAD: %s" %(datetime.now() - absolute_start_time))

            self._print_errors_and_messages()


            self._process_dictionary_into_df()
        except Exception as e:
            print('***')
            print(e)
            self.stop_everything = True
            self.stop()

    def stop(self):
        if globals().get(self.socket_manager_identifier):
            globals()[self.socket_manager_identifier].stop()
            del globals()[self.socket_manager_identifier]


    def stream_status(self):
        if globals().get(self.socket_manager_identifier):
            return globals()[self.socket_manager_identifier].websocket_status
        else:
            return 'DISCONNECTED - NOT RETRYING'

# ____________________________________ PRIVATE METHODS _________________________________


    def _process_timezones(self, df):
        df.index = df.index.tz_localize('utc')

        if self.timezone:
            df.index = df.index.tz_convert(self.timezone)

        return df

    def _process_dictionary_into_df(self):
        for asset in list(self.symbols.keys()):
            self.symbols[asset] = pd.DataFrame(self.symbols[asset])
            self.symbols[asset].index = pd.to_datetime(self.symbols[asset].index, unit='ms')

            if 'SYMBOL' in self.symbols[asset].columns:
                self.symbols[asset] = self.symbols[asset].drop('SYMBOL', 1)

    def _print_errors_and_messages(self):
        for error in self.errors:
            print("Error:! %s" %error)

        for message in self.messages:
            print(message)

    def _query_historical_chunks(self, time_chunks):
        count = 0

        print('Querying for historical data... this could take a while')
        for time_chunk in time_chunks:
            if self.stop_everything:
                self.stop()
                break

            self._query_historical_chunk(time_chunk)
            if self.stop_everything:
                self.stop()
                break
            count = count + 1
#             print("Data Load is %s %% complete " %(round(100 * (count / len(time_chunks)))))

        if self.stop_everything:
            self.stop()
            return

    def _configure_and_start_socket_manager(self):
        if globals().get(self.socket_manager_identifier, False):
            globals()[self.socket_manager_identifier].stop()

        self.sm = SocketManager(lambda x: self._on_message(x), self.ip, self.secret_key, self.public_key, 'AssetChannel', self.params, self.socket_manager_identifier)

        listener_thread = threading.Thread(target=self.sm._run_forever_patch, name=self.exchange)

        listener_thread.start()


    def _get_active_symbols_if_all_specified(self):
         if type(self.requested_symbols) == str and self.requested_symbols.upper() == 'ALL':
            self.requested_symbols = json.loads(self._get('http://%s/api/v1/active_symbols' %(self.ip), {"exchange": self.exchange}).json()['symbols'])

    def _load_configs_and_messages(self):
        response = self._get('http://%s/api/v1/messages_and_configs' %(self.ip), {"message": 'hello'}).json()

        if len(response["messages"]) > 0:
            print('=================== MESSAGES ==================')
            for message in response['messages']:
                print('--' + message + '\n')
            print('===============================================')


        self.chunk_size = self._get_timedelta_from_lookback_period_string(response['chunk_size'])

    def _validate_params(self, params):
        valid_durations = ['s', 'm', 't', 'h', 'd', 'S', 'M', 'T', 'H', 'D']

        invalid_lookback_period = 'INVALID LOOKBACK PERIOD. Must be an integer and duration identifer. Examples: 5s, 6m, 1d .Valid duration identifiers: %s ' %(valid_durations)
        try:
            if params["lookback_period"][-1] not in valid_durations:
                raise Exception(invalid_lookback_period)
        except:
            raise Exception(invalid_lookback_period)

        try:
            if len(params["exchange"]) == 0:
                raise Exception('Must Specify an exchange')
        except:
            raise Exception('Must Specify an exchange')


        try:
            if len(params["symbols"]) == 0:
                raise Exception('Must specify some symbols OR specify "ALL" ')
        except:
            raise Exception('Must specify some symbols OR specify "ALL" ')

        try:
            if len(params['lookback_period']) == 0:
                raise Exception('Must specify a valid lookback_period!')
        except:
            raise Exception('Must specify a valid lookback_period!')


    def _get_timedelta_from_lookback_period_string(self, lookback_period):
        num = int(lookback_period[:-1])
        letter = lookback_period[-1]
        if letter.lower() == 's':
            lookback_period =  timedelta(seconds=num)
        elif letter.lower() == 'm' or letter.lower() == 't':
            lookback_period =  timedelta(minutes=num)
        elif letter.lower() == 'h':
            lookback_period =  timedelta(hours=num)
        elif letter.lower() == 'd':
            lookback_period =  timedelta(days=num)
        else:
            raise Exception('Invalid lookback_period!')

        return lookback_period


    def _generate_time_chunks(self, lookback_period):
        chunks = []
        chunk_size = self.chunk_size

        lookback_period = self._get_timedelta_from_lookback_period_string(lookback_period)


        stop_time = datetime.utcnow()
        start_time = (stop_time - lookback_period)

        if lookback_period > chunk_size:

            end_time = start_time + chunk_size

            while end_time < stop_time:
                chunks.append({ "start_time": str(start_time), "end_time": str(end_time) })

                start_time = end_time
                end_time = end_time + chunk_size

            end_time = datetime.utcnow()

            chunks.append({ "start_time": str(start_time), "end_time": str(end_time) })

        else:

            chunks.append({ "start_time": start_time, "end_time": stop_time  })


        return chunks

    def _get(self, url, params):

        url = url + "?" + urlencode(params)

        headers = {
            "Signature": self._create_signature(self.secret_key, url),
            "Public-Key": self.public_key,
        }


        try:
            response =  requests.get(url, headers=headers)
        except:
            raise Exception('Error connecting to LiveDF - API')


        if response.status_code != 200:
            try:
                print(response.json()['message'])
            except:
                pass

            try:
                print(response.json()['messages'])
            except:
                pass

            try:
                print(response.json()['errors'])
            except:
                pass

            raise Exception('ERROR! CODE: %s' %(response.status_code))

        return response



    def _query_historical_chunk(self, time_chunk):
        url = 'http://%s/api/v1/seed_client' %(self.ip)


        self.start_time = datetime.now()

        params = {
            "exchange": self.exchange,
            "symbols": (',').join(self.requested_symbols),
            "start_time": time_chunk["start_time"],
            "end_time": time_chunk["end_time"]
        }
        response = self._get(url, params = params)



        try:
            response = response.json()
        except:
            raise Exception('ERROR - Error PARSING JSON RESPONSE FOR HISTORICAL DATA FOR %s' % (time_chunk))

#         print("Historical Data loaded in: %s" %(datetime.now() - self.start_time))

        if response.get('message', False):
            self.messages.append(message)

        if response.get('errors', False):
            for error in response["errors"]:
                self.errors.append(error)

        if response.get('messages', False):
            for message in response["messages"]:
                self.messages.append(message)

        for asset in response['payload']:
            if asset not in list(self.symbols.keys()):
                self.symbols[asset] = pd.DataFrame(json.loads(response['payload'][asset]))
                self.symbols[asset].index = pd.to_datetime(self.symbols[asset].index, unit='ms')

                self.symbols[asset] = self._process_timezones(self.symbols[asset])

                self.symbols[asset] = self.symbols[asset].drop_duplicates()
            else:
                historical_df = pd.DataFrame(json.loads(response['payload'][asset]))
                historical_df.index = pd.to_datetime(historical_df.index, unit='ms')


                historical_df = self._process_timezones(historical_df)


                df_columns = historical_df.columns

                # prune symbols columns using the historical_df columns as source of truth (ones to keep)
                for column in [x for x in self.symbols[asset].columns if x not in df_columns and len(df_columns) != 0]:
                    self.symbols[asset] = self.symbols[asset].drop(column, 1)

                self.symbols[asset] = self.symbols[asset].append(historical_df, sort = False).sort_index().drop_duplicates()

    def _append(self, message):
        tick_df = pd.DataFrame(message, index=[message["index"]])
        tick_df.index = pd.to_datetime(tick_df.index)

        tick_df = self._process_timezones(tick_df)

        symbol = message['symbol']

        with self.lock:

            if symbol not in list(self.symbols.keys()):
                self.symbols[symbol] = tick_df
            else:

                if tick_df.index[0] not in self.symbols[symbol].index:

                    df_columns = self.symbols[symbol].columns
                    message_columns = list(message.keys())

                    for column in [x for x in message_columns if x not in df_columns and len(df_columns) != 0]:
                        tick_df = tick_df.drop(column, 1)

                    self.symbols[symbol] = self.symbols[symbol].append(tick_df, sort = False)
                    self.symbols[symbol] = self.symbols[symbol][self.symbols[symbol].index >= self.symbols[symbol].index[-1] - pd.Timedelta(self.lookback_period)]


    def _on_message(self, message):
        message = json.loads(message)

        if message.get('type', False) and message['type'] == 'reject_subscription':
            # HANDLE UNAUTHORIZED HERE
            raise Exception('Subscription Rejected')

        if message.get('message', False):
            message = message['message']

            if type(message) is not int:
                self._append(json.loads(message))

    def _create_signature(self, secret, message):
        message = bytes(message, 'utf-8')
        secret = bytes(secret, 'utf-8')
        hash = hmac.new(secret, message , hashlib.sha256)

        return base64.b64encode(hash.digest())
