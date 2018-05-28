import json
import os
from datetime import date
from pathlib import Path

import requests

from dotplus.config import Config, read_config


class Credentials:
    def __init__(self, token, client_id, config):
        self.token = token
        self.client_id = client_id
        self.config = config


class UrlFactory:
    @classmethod
    def time_cards(cls, url: str, start_date: date, end_date: date) -> str:
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')

        return url.format(start_date, end_date)


class InvalidCredentialsError(Exception):
    pass


def time_cards(start_date: date, end_date: date) -> [dict]:
    config = resolve_config()
    credentials = _login(config)
    return _time_cards(credentials, start_date, end_date)


def resolve_config():
    return read_config(os.path.join(Path.home(), '.dotplusrc'))


def _login(config: Config) -> Credentials:
    credentials = {'login': config.email, 'password': config.password}
    headers = {'api-version': '2', 'content-type': 'application/json;charset=UTF-8'}

    body = json.dumps(credentials)

    response = requests.post(config.sign_in_url, headers=headers, data=body)
    login_data = response.json()

    try:
        return Credentials(login_data['token'], login_data['client_id'], config)
    except KeyError:
        raise InvalidCredentialsError


def _time_cards(credentials: Credentials, start_date: date, end_date: date) -> [dict]:
    url = UrlFactory.time_cards(credentials.config.time_cards_url, start_date, end_date)

    headers = {
        'access-token': credentials.token,
        'client': credentials.client_id,
        'uid': credentials.config.email,
    }

    response = requests.get(url, headers=headers)

    time_cards_data = response.json()
    return [_parse_work_day(w) for w in time_cards_data['work_days']]


def _parse_work_day(work_day):
    result = []
    raw_time_cards = work_day['time_cards']
    for raw_time_card in raw_time_cards:
        result += [raw_time_card['time']]

    return {'date': work_day['date'], 'time_cards': result}
