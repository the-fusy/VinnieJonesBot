import logging

from telegram import bot

from splitwise.behaviour import start


logger = logging.getLogger(__name__)


def start_polling():
    bot_username = bot.get_me().username
    logger.info(f'Start pooling for bot {bot_username}')

    last_update = None

    while True:
        updates = bot.get_updates(timeout=10, offset=last_update)
        for update in sorted(updates, key=lambda update: update.id):
            start(update)
            last_update = update.id + 1
