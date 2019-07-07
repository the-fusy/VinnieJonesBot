from telegram.types import Update

import logging


logger = logging.getLogger(__name__)


def start(update: Update):
    logger.info(update.message.text)
