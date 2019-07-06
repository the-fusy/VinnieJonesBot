from telegram.types import Update


def start(update: Update):
    print(update.message.text)
