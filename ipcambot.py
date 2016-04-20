# -*- coding: utf-8 -*-

import os
from io import BytesIO

import requests
from telebot import TeleBot, types

BOT_TOKEN = 'token'
BOT_NAME = 'bot'
ALLOWED_USERS = []
CAMS = {}

ROOTDIR = os.path.abspath(os.path.dirname(__file__))

try:
    execfile(os.path.join(ROOTDIR, 'settings.py'))
except IOError:
    raise Exception('Missing settings.py file with bot configs')

bot = TeleBot(BOT_TOKEN)


def is_allowed(f):
    """Allowed users only decorator"""

    def wrapped(message):
        if message.from_user.username in ALLOWED_USERS:
            return f(message)
        else:
            bot.reply_to(message, 'Você não pode enviar comandos.')
    return wrapped


@bot.message_handler(commands=['help'])
@is_allowed
def send_help(message):
    """Send help message"""

    help = ('Comandos:\n' +
            '/help  - Esta mensagem de ajuda\n' +
            '/start - Mensagem de boas vindas\n' +
            '/cam - Snapshot das câmeras')

    bot.send_message(message.chat.id, help)


@bot.message_handler(commands=['start'])
@is_allowed
def send_welcome(message):
    """Send welcome message"""

    bot.send_message(message.chat.id,
                     ('Olá eu sou {}!\n' +
                      'Seu assistente de monitoramento.').format(BOT_NAME))


@bot.message_handler(commands=['ping'])
@is_allowed
def ping(message):
    """Checks for bot  response"""

    bot.send_message(message.chat.id, 'pong')


@bot.message_handler(commands=['cam'])
def cam_keyboard(message):
    """Start cam selection keyboard"""

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1)
    keys = [types.KeyboardButton(k) for k in CAMS]

    keyboard.add(*keys)

    msg = bot.reply_to(message, 'Escolha uma câmera:', reply_markup=keyboard)
    bot.register_next_step_handler(msg, get_cam)


def get_cam(message):
    """Get cam snapshot"""

    cam = CAMS.get(message.text)

    if cam:
        url = 'http://{user}:{password}@{ip}{path}'.format(**cam)

        response = requests.get(url)

        # start chat photo upload
        bot.send_chat_action(message.chat.id, 'upload_photo')

        # create Byte stream
        file = BytesIO(response.content)
        # add name to validate telegram extension check
        file.name = 'snapshot.jpg'

        # send the actual snapshot
        bot.send_photo(message.chat.id, file)

        file.close()
    else:
        bot.reply_to(message, 'Câmera inexistente')


bot.polling()
