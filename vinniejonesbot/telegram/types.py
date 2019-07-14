from typing import Optional

import io
import requests
import logging

from PIL import Image

from django.conf import settings


logger = logging.getLogger(__name__)


class BaseType():
    def __new__(cls, data):
        if not data:
            return None
        return super().__new__(cls)


class User(BaseType):
    def __init__(self, data):
        self.id: int = data['id']
        self.username: Optional[str] = data.get('username')


class Chat(User):
    pass


class File(BaseType):
    def __init__(self, data):
        self.file_id: str = data['file_id']
        self.file_size: int = data.get('file_size')
        self.file_path: str = data.get('file_path')
        url = f'https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{self.file_path}'
        self.file: Image = Image.open(requests.get(url, stream=True).raw)


class Message(BaseType):
    def __init__(self, data):
        self.id: int = data['message_id']
        self.user: Optional[User] = User(data.get('from'))
        self.date: int = data['date']
        self.chat: Chat = Chat(data['chat'])
        self.text: str = data.get('text')
        self.photo: str = None
        mxwh = -1
        for ph in data.get('photo', []):
            if ph['width'] > mxwh:
                mxwh = ph['width']
                self.photo: str = ph['file_id']


class CallbackQuery(BaseType):
    def __init__(self, data):
        self.id: int = data['id']
        self.user: User = User(data.get('from'))
        self.message: Optional[Message] = Message(data.get('message'))
        self.data: str = data['data']


class Update(BaseType):
    types = ['message', 'callback_query']

    def __init__(self, data):
        self.id: int = data['update_id']
        self.message: Optional[Message] = Message(data.get('message'))
        self.callback_query: Optional[CallbackQuery] = CallbackQuery(data.get('callback_query'))

        for t in self.types:
            if getattr(self, t, None) is not None:
                self.type = t
                break
