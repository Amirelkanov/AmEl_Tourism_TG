#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import ceil

from telebot import types

from data.articles import Category, Article
from data.user_info import TGUserInfo
from extensions.const import max_num_of_categories_per_page, article_url
from extensions.formatting_distance import lonlat_distance


def get_categories_kb(session, user_id: int):
    """
    :param session: SQLAlchemy session object
    :param user_id: id of current user
    :return: inline category keyboard
    """

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Adding categories
    categories = sorted(session.query(Category).all(),
                        key=lambda x: x.name_of_category)
    page = session.query(TGUserInfo).filter_by(id=user_id).first().page
    for category in (categories[
                     max_num_of_categories_per_page * (page - 1):
                     max_num_of_categories_per_page * page]):
        keyboard.add(types.InlineKeyboardButton(text=category.name_of_category))

    # Adding nav arrows
    arrows = []
    if page > 1:
        arrows.append(types.InlineKeyboardButton(text="«"))
    if ceil(len(categories) / max_num_of_categories_per_page) > page:
        arrows.append(types.InlineKeyboardButton(text="»"))

    keyboard.row(*arrows)
    keyboard.add(types.KeyboardButton(text="🌎 Место", request_location=True))

    return keyboard


def get_articles_kb(session, category_id: int, user_id: int):
    """
    :param session: SQLAlchemy session object
    :param category_id: id of the category by which articles will be searched
    :param user_id: id of current user
    :return: inline category keyboard and name of category
    """

    keyboard = types.InlineKeyboardMarkup()

    # Formatting the user coords
    coords = list(map(float, session.query(TGUserInfo).filter_by(
        id=user_id).first().coords.split(", ")))

    # Sorting places by proximity to the user
    articles = sorted(session.query(Article).filter_by(
        article_category_id=category_id).all(),
                      key=lambda x: lonlat_distance(coords, list(
                          map(float, x.coords.split(", ")))), reverse=True)[:5]

    # Adding articles
    for article in articles:
        keyboard.add(types.InlineKeyboardButton(text=f"{article.title}",
                                                url=f"{article_url}/"
                                                    f"{article.id}"))
    return keyboard, articles
