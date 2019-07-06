import logging

from django.core.management.base import BaseCommand

from telegram.polling import start_polling


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        while True:
            try:
                start_polling()
            except:
                logger.exception('Error while polling')
