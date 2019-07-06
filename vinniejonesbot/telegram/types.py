from typing import Optional


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


class Message(BaseType):
    def __init__(self, data):
        self.id: int = data['message_id']
        self.user: Optional[User] = User(data.get('from'))
        self.date: int = data['date']
        self.chat: Chat = Chat(data['chat'])
        self.text: str = data.get('text')


class Update(BaseType):
    def __init__(self, data):
        self.id: int = data['update_id']
        self.message: Optional[Message] = Message(data.get('message'))
