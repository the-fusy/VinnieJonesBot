import logging

import json
import requests

from functools import partial

from telegram.types import User, Message, Update


logger = logging.getLogger(__name__)


class Bot():
    available_methods = {
        'getme': User,
        'sendmessage': Message,
        'getupdates': Update,
    }

    def __init__(self, token):
        self.token = token

    def make_request(self, method, **data):
        if method not in self.available_methods.keys():
            logger.error(f'Unsupported method {method}')
            return None

        logger.debug(f'Making telegram request ({method}) with data: {data}')

        response = requests.post(
            url=f'https://api.telegram.org/bot{self.token}/{method}',
            json=data,
            timeout=2,
        ).json()

        if not response['ok']:
            logger.error(
                f'Error ({response.get("error_code")}, {response.get("description")}) while making {method}: {data}'
            )

        response_type = self.available_methods[method]

        if isinstance(response['result'], list):
            return [response_type(item) for item in response['result']]
        return response_type(response['result'])

    def __getattr__(self, name):
        if '_' in name:
            name = name.replace('_', '').lower()
        if name in self.available_methods.keys():
            return partial(self.make_request, method=name)
