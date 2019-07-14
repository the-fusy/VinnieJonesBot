from pyzbar import pyzbar

from django.db.models import F

from fns.api import FnsApi
from fns.models import FnsUser
from splitwise.models import User, Item, ShoppingListUser
from telegram.models import TelegramUser, states
from telegram.types import Update
from telegram import bot

import logging


logger = logging.getLogger(__name__)


def start(update: Update):
    tg_user = getattr(update, update.type).user  # TODO: get tg_user
    if not User.objects.filter(telegram__user_id=tg_user.id).exists():
        user = User(
            telegram=TelegramUser.objects.create(
                user_id=tg_user.id,
                login=tg_user.username,
            ),
            fns=FnsUser.objects.create(),
        )
        user.save()
    else:
        user = User.objects.get(telegram__user_id=tg_user.id)
    # TODO: check splitwise token and ask it if invalid

    if update.type == 'callback_query':
        if 'approve' in update.callback_query.data:
            approve = update.callback_query.data == 'approve'
            ShoppingListUser.objects.filter(message_id=update.callback_query.message.id).update(approve=approve)
        else:
            item_id, value = list(map(int, update.callback_query.data.split('_')))
            Item.objects.get(id=item_id).change_count(user, value)
    else:
        globals()[f'process_{user.telegram.state}'](user, update)


def process_main(user, update):
    if not update.message and not user.last_query:
        logger.error(f'Some weird behaviour. user: {user}, update: {update}')
        return

    qr_text = None
    if not update.message:
        qr_text = user.last_query
    if not qr_text and update.message.photo:
        photo = bot.get_file(file_id=update.message.photo)
        data = pyzbar.decode(photo.file)
        if data:
            qr_text = data[0].data.decode('utf-8')
    if not qr_text and update.message.text:
        qr_text = update.message.text

    if not qr_text:
        user.telegram.send_message(text='Не удалось разобрать QR, попробуйте ещё раз')
        return

    user.last_query = qr_text
    user.save()

    fns = FnsApi(user.fns)
    if not fns.is_authenticated():
        user.telegram.change_state(states.GET_FNS_NUMBER)
        return

    shopping_list = fns.get_shopping_list(qr_text)
    if not shopping_list:
        user.telegram.send_message(text='Такой код не найден в системе')
    else:
        shopping_list.set_payer(user)
        shopping_list.add_user(user)

    user.last_query = None
    user.save()


def process_get_fns_number(user, update):
    number = update.message.text or 'undefined'

    user.fns.phone = number

    try:
        user.fns.save()
    except ValueError:
        user.telegram.send_message(text='Что за фигня?! Введи нормально')
        return

    if not FnsApi(user.fns).send_password():
        user.telegram.send_message(text='Кажется у нас проблемы...')
        user.telegram.change_state(states.MAIN)
    else:
        user.telegram.change_state(states.GET_FNS_PASSWORD)


def process_get_fns_password(user, update):
    pswd = update.message.text

    user.fns.password = pswd
    user.fns.save()

    if FnsApi(user.fns).is_authenticated():
        user.telegram.change_state(states.MAIN)
        process_main(user, Update({'update_id': -1}))
    else:
        user.telegram.send_message(text='Что-то введено неверно')
        user.telegram.change_state(states.GET_FNS_NUMBER)
