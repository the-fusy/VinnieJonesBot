from django.db import models

from telegram import bot


class States():
    states = (
        'main',
        ('get_fns_number', 'Введите номер телефона'),
        ('get_fns_password', 'Введите пароль из смс'),
    )

    def __init__(self, user=None):
        self.messages = {}
        for state in self.states:
            message = None
            if type(state) != str:
                message = state[1]
                state = state[0]
            setattr(self, state.upper(), state.lower())
            self.messages[state.lower()] = message
        self.user = user

    def __call__(self):
        django_states = []
        for state in self.states:
            state = state[0] if type(state) != str else state
            django_states.append((state.upper(), state.lower()))
        return django_states

states = States()


class TelegramUser(models.Model):
    user_id = models.IntegerField(unique=True)
    login = models.CharField(max_length=128, unique=True, null=True, blank=True)
    state = models.CharField(choices=states(), max_length=128, default=states.MAIN)

    def send_message(self, **data):
        return bot.send_message(chat_id=self.user_id, **data)

    def edit_message(self, **data):
        return bot.edit_message_text(chat_id=self.user_id, **data)

    def change_state(self, state):
        if states.messages[state]:
            self.send_message(text=states.messages[state])
        self.state = state
        self.save()
