from django.db import models


class TelegramUser(models.Model):
    user_id = models.IntegerField(unique=True)
    login = models.CharField(max_length=128, unique=True, null=True, blank=True)
