from typing import Optional, List
import logging

import time
import dateutil
import random
import string

import json
import requests

from decimal import Decimal

from django.conf import settings

from fns.models import FnsUser
from splitwise.models import Item


logger = logging.getLogger(__name__)


class FnsApi():
    def __init__(self, phone, password):
        self.phone = phone
        self.password = password

    def is_authenticated(self) -> bool:
        if not self.phone or not self.password:
            return False

        response = requests.get(
            url=f'{settings.FNS_HOST}/mobile/users/login',
            auth=(self.phone, self.password),
            timeout=2,
        )

        return response.status_code == 200

    def send_password(self) -> bool:
        logger.info(f'Trying to send password to phone: {self.phone}')

        if not self.phone:
            return False

        name = [random.choice(string.ascii_lowercase) for i in range(8)]

        response = requests.post(
            url=f'{settings.FNS_HOST}/mobile/users/signup',
            json={'phone': self.phone, 'name': name, 'email': f'{name}@mail.ru'},
            timeout=2,
        )

        if response.status_code == 204:
            logger.info(f'Registered and sent password to phone: {self.phone}')
            return True

        response = requests.post(
            url=f'{settings.FNS_HOST}/mobile/users/restore',
            json={'phone': self.phone},
            timeout=2,
        )

        if response.status_code == 204:
            logger.info(f'Sent password to phone: {self.phone}')
            return True

        logger.error(f'Bad status code ({response.status_code}) while sending password to phone: {self.phone}')

        return response.status_code == 204

    def get_receipt(self, qr_text, second_attempt=False) -> Optional[List[Item]]:
        logger.info(f'Trying to get receipt: {qr_text}')

        params = {
            key: value
            for key, value in [item.split('=') for item in qr_text.split('&')]
        }
        params['s'] = params['s'].replace('.', '')

        response = requests.get(
            url='{host}/ofds/*/inns/*/fss/{fn}/operations/{n}/tickets/{i}?fiscalSign={fp}&date={t}&sum={s}'.format(
                host=settings.FNS_HOST,
                **params,
            ),
            auth=(self.phone, self.password),
        )

        if response.status_code != 204:
            logger.error(f'Bad status code ({response.status_code}) while checking the receipt: {qr_text}')
            return None

        time.sleep(3)

        response = requests.get(
            url='{host}/inns/*/kkts/*/fss/{fn}/tickets/{i}?fiscalSign={fp}&sendToEmail=no'.format(
                host=settings.FNS_HOST,
                **params,
            ),
            auth=(self.phone, self.password),
            headers={'device-id': '', 'device-os': ''},
        )

        if response.status_code != 200:
            if second_attempt:
                logger.error(f'Bad status code ({response.status_code}) while getting the receipt: {qr_text}')
                return None
            else:
                time.sleep(3)
                return self.get_receipt(qr_text, True)

        try:
            items = response.json()['document']['receipt']['items']
        except (json.JSONDecodeError, KeyError):
            logger.exception(f'Error while parsing response with items: {response.content}')
            return None

        return [
            Item(
                name=item['name'],
                price=item['price'],
                count=Decimal(item['quantity']),
                total_price=item['sum'],
            )
            for item in items
        ]
