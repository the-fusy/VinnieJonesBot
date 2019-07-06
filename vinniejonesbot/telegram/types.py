from typing import Optional


class User():
    def __init__(self, data):
        self.id: int = data['id']
        self.username: Optional[str] = data.get('username')


class Chat(User):
    pass


class Message():
    def __init__(self, data):
        self.id: int = data['message_id']
        self.user: Optional[User] = User(data['from'])
        self.date: int = data['date']
        self.chat: Chat = Chat(data['chat'])
        self.text: str = data.get('text')


class Update():
    def __init__(self, data):
        self.id: int = data['update_id']
        self.message: Optional[Message] = Message(data['message'])
