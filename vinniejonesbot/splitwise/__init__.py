from fns.api import FnsApi
from splitwise.models import User
from telegram.models import TelegramUser
from telegram.types import Update
from telegram import bot


logger = logging.getLogger(__name__)


def process_main(user, update):
    if not update.message and not user.last_query:
        logger.error(f'Some weird behaviour. user: {user}, update: {update}')
        return

    qr_text = None
    if not update.message:
        qr_text = user.last_query
    if update.message.photo:
        photo = bot.get_file(file_id=update.message.photo)
        # TODO: qr_text = parse_qr(photo.file)
    if not qr_text and update.message.text:
        qr_text = update.message.text

    if not qr_text:
        user.send_message(text='Не удалось разобрать QR, попробуйте ещё раз')
        return

    user.last_query = qr_text
    user.save()

    fns = FnsApi(user.fns)
    if not fns.is_authenticated():
        change_state(user, 'get_fns_number')
        return

    receipt = fns.get_receipt(qr_text)
    user.send_message(text=str([item.__dict__ for item in receipt]))
    user.last_query = None
    user.save()

def proccess_get_fns_number(user, update):
    number = update.message.text or 'undefined'

    user.fns.phone = number

    try:
        user.fns.save()
    except ValueError:
        user.send_message(text='Что за фигня?! Введи нормально')
        return

    if not FnsApi(user.fns).send_password():
        user.send_message(text='Кажется у нас проблемы...')
        change_state(user, 'main')
    else:
        change_state(user, 'get_fns_password')

def process_get_fns_password(user, update):
    pswd = update.message.text

    user.fns.password = pswd
    user.fns.save()

    if FnsApi(user.fns).is_authenticated():
        change_state(user, 'main')
        process_main(user, Update({'update_id': -1}))
    else:
        user.send_message(text='Что-то введено неверно')
        change_state(user, 'get_fns_number')


STATES_MAP = {
    'main': process_main,
    'get_fns_number': proccess_get_fns_number,
    'get_fns_password': process_get_fns_password,
}

MESSAGES_MAP = {
    'get_fns_number': 'Введите номер телефона',
    'get_fns_password': 'Введите пароль из смс'
}

def change_state(user, state):
    if MESSAGES_MAP[state]:
        user.telegram.send_message(text=MESSAGES_MAP[state])
    user.state = state
    user.save()

def start(update):
    tg_user = update.message.user # TODO: get tg_user
    if not User.objects.filter(telegram__user_id=tg_user.id).exists():
        user = User(
            telegram=TelegramUser(
                user_id=tg_user.id,
                login=tg_user.username,
            ),
            state='main',
        )
        user.save()
    else:
        user = User.objects.filter(telegram__user_id=tg_user.id)[0]
    # TODO: check splitwise token and ask it if invalid
    STATES_MAP[user.state](user, update)

