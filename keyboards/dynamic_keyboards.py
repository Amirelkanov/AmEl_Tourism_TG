#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import ceil

from telebot import types

from data.articles import Category, Article
from data.user import UserInfo
from extensions.const import max_num_of_categories_per_page, article_url
from extensions.formatting_distance import lonlat_distance


def get_categories_kb(session, user_id: int):
    """
    :param session: SQLAlchemy session object
    :param user_id: id of current user
    :return: inline category keyboard
    """

    keyboard = types.InlineKeyboardMarkup()

    # Adding categories
    categories = session.query(Category).all()
    page = session.query(UserInfo).filter_by(user_id=user_id).first().page
    for category in (categories[
                     max_num_of_categories_per_page * (page - 1):
                     max_num_of_categories_per_page * page]):
        keyboard.add(types.InlineKeyboardButton(text=category.name_of_category,
                                                callback_data=f"{category.id}"))

    # Adding nav arrows
    arrows = []
    if page > 1:
        arrows.append(types.InlineKeyboardButton(text="«",
                                                 callback_data=f"page "
                                                               f"{page - 1}"))
    if ceil(len(categories) / max_num_of_categories_per_page) > page:
        arrows.append(types.InlineKeyboardButton(text="»",
                                                 callback_data=f"page "
                                                               f"{page + 1}"))
    keyboard.row(*arrows)

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
    coords = list(map(float, session.query(UserInfo).filter_by(
        user_id=user_id).first().coords.split(", ")))

    # Sorting places by proximity to the user
    articles = sorted(session.query(Article).filter_by(
        article_category_id=category_id).all(),
                      key=lambda x: lonlat_distance(coords, list(
                          map(float, x.coords.split(", ")))), reverse=True)[:5]

    for article in articles:
        keyboard.add(types.InlineKeyboardButton(text=f"{article.title}",
                                                url=f"{article_url}/"
                                                    f"{article.id}"))
    return keyboard, session.query(Category).filter_by(
        id=category_id).first().name_of_category, articles
