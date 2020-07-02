#!/usr/bin/python
# -*- coding: utf-8 -*-

import telebot
from telebot.apihelper import ApiException

from data.db_session import global_init, create_session
from data.user import UserInfo
from extensions.const import SQLALCHEMY_DATABASE_URI
from extensions.token import TELEGRAM_BOT_TOKEN
from keyboards.dynamic_keyboards import get_categories_kb, get_articles_kb
from keyboards.static_keyboards import location_kb

# Init TG bot
bot = telebot.TeleBot(token=TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=["start"])
def greeting(message):
    """ Greeting function """

    bot.send_message(message.chat.id, "Привет! Я телеграм - бот, призванный "
                                      "помогать туристам!\n\n"
                                      "_Для начала нужно дать доступ к "
                                      "местоположению._",
                     parse_mode="markdown", reply_markup=location_kb())


@bot.message_handler(content_types=["location"])
def location(message):
    """ User geolocation processing """

    session = create_session()

    user = session.query(UserInfo).filter_by(user_id=message.chat.id).first()

    user_info = UserInfo() if not user else user
    user_info.user_id = message.chat.id
    user_info.coords = f"{message.location.latitude}, " \
                       f"{message.location.longitude}"
    user_info.page = 1
    session.add(user_info)
    session.commit()

    bot.send_message(message.chat.id, "📍 Геопозиция получена! С чего начнем?",
                     reply_markup=get_categories_kb(session,
                                                    message.chat.id))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """ Function handling inline callback """

    session = create_session()
    user = session.query(UserInfo).filter_by(
        user_id=call.message.chat.id).first()

    if call.message:
        # Pagination implementation
        if call.data.find("page") != -1:

            user.page = int(call.data.split()[-1])
            session.add(user)
            session.commit()

            try:
                bot.edit_message_reply_markup(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=get_categories_kb(session,
                                                   call.message.chat.id)
                )
            except ApiException:
                pass

        # Returning articles by category to the user
        else:
            kb, category, articles = get_articles_kb(session, int(call.data),
                                                     call.message.chat.id)
            bot.send_message(chat_id=call.message.chat.id,
                             text=f"Ближайшие {category.lower()}:" if articles
                             else "Ничего не найдено 👀",
                             reply_markup=kb)


# Launching app
if __name__ == "__main__":
    global_init(SQLALCHEMY_DATABASE_URI)
    bot.infinity_polling(timeout=3)
