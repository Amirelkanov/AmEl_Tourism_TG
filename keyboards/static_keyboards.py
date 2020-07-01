#!/usr/bin/python
# -*- coding: utf-8 -*-

from telebot import types


def location_kb():
    """
    :return: keyboard which prompts for the location
    """

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
    keyboard.add(types.KeyboardButton(text="🌎 Место", request_location=True))
    return keyboard
