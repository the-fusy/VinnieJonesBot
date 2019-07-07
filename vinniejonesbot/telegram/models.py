from django.db import models

from telegram import bot


class TelegramUser(models.Model):
    user_id = models.IntegerField(unique=True)
    login = models.CharField(max_length=128, unique=True, null=True, blank=True)

    def send_message(self, **data):
        return bot.send_message(chat_id=self.user_id, **data)

