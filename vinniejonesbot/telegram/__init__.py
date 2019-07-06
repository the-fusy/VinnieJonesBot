from django.conf import settings

from telegram.bot import Bot


bot = Bot(settings.BOT_TOKEN)
