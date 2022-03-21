import datetime as dt
import logging

import requests
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import SPORTS, DATE_F, MC_URL, HEADERS
from .callback_datas import *
#Получение клавиатуры с доступными видами спорта
def get_sport_menu() -> InlineKeyboardMarkup:

    sport_menu = InlineKeyboardMarkup(row_width = 1)

    for key, value in SPORTS.items():

        sport_menu.insert(InlineKeyboardButton(text = value,
                                              callback_data = sport_cb.new(sport = key)))

    return sport_menu

#Получение клавиатуры с ближайшими датами (Сегодня, Вчера, Завтра)
def get_date_menu(cb : str) -> InlineKeyboardMarkup:

    today = dt.datetime.today().strftime(DATE_F)
    tomorrow = (dt.datetime.today() + dt.timedelta(days = 1)).strftime(DATE_F)
    yesterday = (dt.datetime.today() - dt.timedelta(days = 1)).strftime(DATE_F)

    sport = sport_cb.parse(cb)['sport']
    date_menu = InlineKeyboardMarkup(inline_keyboard = [
        [
            InlineKeyboardButton(text = "📅Сегодня📅",
                                 callback_data = date_cb.new(sport = sport,
                                                            date = today))
        ],
        [
            InlineKeyboardButton(text = "📅Вчера📅",
                                 callback_data = date_cb.new(sport = sport,
                                                            date = yesterday)),
            InlineKeyboardButton(text = "📅Завтра📅",
                                 callback_data = date_cb.new(sport = sport,
                                                            date = tomorrow))
        ],
        [
            InlineKeyboardButton(text = "Другие дни",
                                 callback_data = date_cb.new(sport = sport,
                                                             date = "other"))
        ],
        [
            InlineKeyboardButton(text= "Назад↩",
                                 callback_data = "schedule")
        ]
    ])

    return date_menu

#Получение клавиатуры с со всеми датами (Неделю до сегодня, неделю - после)
def get_other_days_menu(cb : str) -> InlineKeyboardMarkup:

    sport = date_cb.parse(cb)['sport']
    other_days_menu = InlineKeyboardMarkup(row_width = 3)

    week_ago = dt.datetime.today() - dt.timedelta(weeks = 1)
    days = [(week_ago + dt.timedelta(days = i)).strftime(DATE_F) for i in range(15)]

    for day in days:

        btn = InlineKeyboardButton(text = day,
                                   callback_data = date_cb.new(sport = sport,
                                                               date = day))
        other_days_menu.insert(btn)

    other_days_menu.add(InlineKeyboardButton(text= "Назад↩",
                                     callback_data = "schedule"))

    return other_days_menu

#Получение меню выбора чемпионата
def get_champ_menu(cb : str) -> InlineKeyboardMarkup:

    sport = date_cb.parse(cb)['sport']
    date = date_cb.parse(cb)['date']
    champ_menu = InlineKeyboardMarkup(row_width = 1)
    url = MC_URL.format(date = date)
    champs = {}

    response = requests.get(url = url,
                            headers = HEADERS)

    logging.info(f"url = {url}, response code = {response.status_code}")

    try:
        champs = response.json()['matches'][sport]['tournaments']
    except KeyError:
        pass

    for champ in champs.values():

        if champ['is_top']:

            btn = InlineKeyboardButton(text = champ['name'],
                                       callback_data = champ_cb.new(sport = sport,
                                                                    date = date,
                                                                    champ_id = champ['id']))
            champ_menu.add(btn)

    champ_menu.add(InlineKeyboardButton(text = "Назад↩",
                                       callback_data = sport_cb.new(sport = sport)))

    return champ_menu

#Получение меню выбора матча
def get_match_btn(cb : str,
                  match_id : str,
                  match_num : int) -> InlineKeyboardMarkup:

    sport = champ_cb.parse(cb)['sport']
    date = champ_cb.parse(cb)['date']
    champ_id = champ_cb.parse(cb)['champ_id']

    btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = "⬆Выбрать⬆",
                               callback_data = match_cb.new(sport = sport,
                                                            date = date,
                                                            champ_id = champ_id,
                                                            match_id = match_id,
                                                            match_num = match_num,
                                                            review_type = "_"))]])

    return btn

#Получение меню продолжения поиска
def get_new_find_menu(cb : str) -> InlineKeyboardMarkup:

    sport = champ_cb.parse(cb)['sport']
    date = champ_cb.parse(cb)['date']
    keyboard = InlineKeyboardMarkup(inline_keyboard =
    [[InlineKeyboardButton(text = "🏅 Вид спорта 🏅",
                           callback_data = "schedule")],
     [InlineKeyboardButton(text = "📅 Дата 📅",
                           callback_data = sport_cb.new(sport = sport))],
     [InlineKeyboardButton(text = "🏆 Чемпионат 🏆",
                           callback_data = date_cb.new(sport = sport,
                                                       date = date))]
    ])

    return keyboard

def get_review_type_menu(cb : str) -> InlineKeyboardMarkup:

    sport = match_cb.parse(cb)['sport']
    date = match_cb.parse(cb)['date']
    champ_id = match_cb.parse(cb)['champ_id']
    match_id = match_cb.parse(cb)['match_id']
    match_num = int(match_cb.parse(cb)['match_num'])

    review_menu = InlineKeyboardMarkup(row_width = 3)
    review_menu.insert(InlineKeyboardButton(text = "Последние матчи",
                                        callback_data = match_cb.new(sport = sport,
                                                                     date = date,
                                                                     champ_id = champ_id,
                                                                     match_id = match_id,
                                                                     match_num = match_num,
                                                                     review_type = 'last')))
    review_menu.insert(InlineKeyboardButton(text = "Очные встречи",
                                        callback_data=match_cb.new(sport=sport,
                                                                  date=date,
                                                                  champ_id=champ_id,
                                                                  match_id=match_id,
                                                                  match_num=match_num,
                                                                  review_type='h2h')))
    review_menu.insert(InlineKeyboardButton(text="Прогноз",
                                        callback_data=match_cb.new(sport=sport,
                                                                   date=date,
                                                                   champ_id=champ_id,
                                                                   match_id=match_id,
                                                                   match_num=match_num,
                                                                   review_type='fore')))



    return review_menu



