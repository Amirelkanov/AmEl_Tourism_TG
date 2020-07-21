#!/usr/bin/python
# -*- coding: utf-8 -*-

import telebot

from data import Category
from data.db_session import global_init, create_session
from data.user_info import TGUserInfo
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

    user = session.query(TGUserInfo).filter_by(id=message.chat.id).first()

    user_info = TGUserInfo() if not user else user
    user_info.id = message.chat.id
    user_info.coords = f"{message.location.latitude}, " \
                       f"{message.location.longitude}"
    user_info.page = 1
    session.add(user_info)
    session.commit()

    bot.send_message(message.chat.id, "🌎 Геопозиция получена! С чего начнем?",
                     reply_markup=get_categories_kb(session,
                                                    message.chat.id))


@bot.message_handler(content_types=["text"])
def categories_handler(message):
    """ Function that processes a query related to categories """

    message_text, user_id = message.text, message.chat.id

    session = create_session()
    user = session.query(TGUserInfo).filter_by(id=user_id).first()

    if message_text in ["«", "»"]:

        user.page = user.page - 1 if message_text == "«" else user.page + 1
        session.add(user)
        session.commit()

        bot.send_message(
            chat_id=user_id,
            text=f"Перелистываем...",
            reply_markup=get_categories_kb(session, user_id),
        )

    elif message_text in list(map(lambda x: x.name_of_category,
                                  session.query(Category).all())):

        kb, articles = get_articles_kb(
            session, session.query(Category).filter_by(
                name_of_category=message_text).first().id,
            user_id)

        bot.send_message(
            chat_id=user_id,
            text=f"Ближайшие {message_text.lower()}:"
            if articles else "Ничего не найдено 👀",
            reply_markup=kb,
        )


# Launching app
if __name__ == "__main__":
    global_init(SQLALCHEMY_DATABASE_URI)  # Init DB
    bot.infinity_polling(timeout=3)
