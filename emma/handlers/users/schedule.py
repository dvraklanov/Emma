import logging
from pprint import pformat, pprint
import time

import requests
from aiogram.types import Message, CallbackQuery

from loader import dp

from data.config import SPORTS, MC_URL, HEADERS, FORECAST_RATE
from utils import get_match_info, compare_score
from keyboards.default import schedule_txt
from keyboards.inline import sport_cb, \
    date_cb, \
    champ_cb, \
    match_cb, \
    get_match_btn, \
    get_champ_menu, \
    get_date_menu, \
    get_other_days_menu, \
    get_new_find_menu, \
    get_sport_menu, \
    get_review_type_menu

"""Handler для раздела 'Расписание'"""

#Переход в меню выбора вида спорта
@dp.message_handler(text = schedule_txt)
@dp.callback_query_handler(text = 'schedule')
async def sport_show(message : [Message, CallbackQuery]):

    text = "🏅 Выбирете желаемый вид спорта"
    if type(message) == Message:
        logging.info(f"cb = {message.text} user_id = {message['chat']['id']} username = {message['chat']['username']}")
        await message.answer(text = text,
                             reply_markup = get_sport_menu())

    else:
        logging.info(f"cb = {message.data} user_id = {message.message['chat']['id']} username = {message.message['chat']['username']}")
        await message.message.edit_text(text = text,
                                        reply_markup = get_sport_menu())

#Переход в меню выбора даты
@dp.callback_query_handler(sport_cb.filter())
async def date_show(cb: CallbackQuery):

    logging.info(f"cb = {cb.data} user_id = {cb.message['chat']['id']} username = {cb.message['chat']['username']}")

    sport = SPORTS[sport_cb.parse(cb.data)['sport']]

    text = f"🏅 Вид спорта: {sport}\n\n " \
           f"📅 Выберете дату события"

    await cb.message.edit_text(text = text,
                               reply_markup = get_date_menu(cb = cb.data))

#Выбор чемпионата
@dp.callback_query_handler(date_cb.filter())
async def champ_show(cb : CallbackQuery):

    logging.info(f"cb = {cb.data} user_id = {cb.message['chat']['id']} username = {cb.message['chat']['username']}")

    sport = SPORTS[date_cb.parse(cb.data)['sport']]
    date = date_cb.parse(cb.data)['date']

    if date != 'other':

        text = f"🏅 Вид спорта: {sport}\n\n " \
               f"📅 Дата: {date}\n\n" \
               f"🏆 Выберите чемпионат"

        await cb.message.edit_text(text = text,
                                   reply_markup = get_champ_menu(cb = cb.data))

    else:

        text = f"🏅 Вид спорта: {sport}\n\n " \
               f"📅 Вьбирете дату события"

        await cb.message.edit_text(text = text,
                                   reply_markup = get_other_days_menu(cb = cb.data))

#Выбор матча
@dp.callback_query_handler(champ_cb.filter())
async def matches_show(cb : CallbackQuery):

    logging.info(f"cb = {cb.data} user_id = {cb.message['chat']['id']} username = {cb.message['chat']['username']}")

    sport = champ_cb.parse(cb.data)['sport']
    sport_name = SPORTS[sport]
    date = champ_cb.parse(cb.data)['date']
    champ_id = champ_cb.parse(cb.data)['champ_id']

    url = MC_URL.format(date=date)
    response = requests.get(url=url,
                            headers=HEADERS)
    logging.info(f"url = {url}, response code = {response.status_code}")

    champ = response.json()['matches'][sport]['tournaments'][f'{sport}-{champ_id}']

    text = f'🏅 Вид спорта: {sport_name}\n\n' \
           f'📅 Дата: {date}\n\n' \
           f'🏆 Чемпионат: {champ["name"]}\n\n' \
           f'🎫 Выберете матч'

    await cb.message.edit_text(text=text)

    for num, match in enumerate(champ['matches']):

        #logging.info(f"match_data = {pformat(match)}")

        text = f"{match['teams'][0]['name']} - {match['teams'][1]['name']}\n\n" \
               f"Статус: {match['status']}"

        if match['status'] == "Окончен":

            text += f'\n\n{match["result"]["detailed"]["goal1"]} - {match["result"]["detailed"]["goal2"]}'

            extra = match['result']['detailed']['extra']
            if extra: text += f"(\n\n({extra}))"

        elif match['status'] == "Не начался":

            text += f"\n\n🕐 Время: {match['time']}"

        await cb.message.answer(text=text,
                                reply_markup=get_match_btn(cb = cb.data,
                                                           match_id = match['id'],
                                                           match_num = num))

    text = f"✔ Кол-во матчей: {len(champ['matches'])}\n\n" \
           f"Вы можете вернуться к поиску 🔎"

    await cb.message.answer(text=text,
                            reply_markup=get_new_find_menu(cb.data))

#Переход к аналитике/статистике
@dp.callback_query_handler(match_cb.filter(review_type = "_"))
async def match_choice(cb : CallbackQuery):

    logging.info(f"cb = {cb.data} user_id = {cb.message['chat']['id']} username = {cb.message['chat']['username']}")
    text = cb.message.text

    if "Окончен" in cb.message.text:

        match_info = get_match_info(cb = cb.data)
        text += "\n\n📊 Статистика 📊"

        for title, stat in match_info['stat'].items():

            home, away = stat.values()
            text += f"\n\n-----{title}----" \
                    f"\n{compare_score([home, away])}  {home} --- {away}  {compare_score([away, home])}"

        await cb.message.edit_text(text=text)

    else:

        text += "\n\n📈 Аналитика 📈"
        await cb.message.edit_text(text = text,
                                   reply_markup = get_review_type_menu(cb = cb.data))

@dp.callback_query_handler(match_cb.filter())
async def match_review(cb : CallbackQuery):

    logging.info(f"cb = {cb.data} user_id = {cb.message['chat']['id']} username = {cb.message['chat']['username']}")
    teams = cb.message.text.split('\n\n')[0].split(" - ")
    text = '\n\n'.join(cb.message.text.split('\n\n')[:4])
    reply_markup = cb.message.reply_markup

    review_type = match_cb.parse(cb.data)['review_type']
    match_info = get_match_info(cb = cb.data)
    pprint(match_info)

    if review_type == 'last':

        if match_info['home']['avg'] and match_info['away']['avg']:

            text += '\n\nРезультаты последних матчей:' \
                    f'\n\n{match_info["home"]["order"]} --- {match_info["away"]["order"]}'\
                    '\n\nТотал:' \
                    f"\n{match_info['home']['total']['mut']} --- {match_info['away']['total']['mut']}" \
                    f"\n\nИндивидуальный тотал:" \
                    f"\n{match_info['home']['total']['self']} --- {match_info['away']['total']['self']}"

            if len(match_info['home']['avg'].keys()) > len(match_info['away']['avg'].keys()): titles = list(match_info['home']['avg'].keys())
            else: titles = list(match_info['away']['avg'].keys())

            for title in titles:

                if title in match_info['home']['avg'] and title in match_info['away']['avg']:

                    home = match_info['home']['avg'][title]['home']
                    away = match_info['away']['avg'][title]['home']

                    text += f'\n\n-----{title}-----' \
                            f'\n{compare_score([home, away])}  {home} --- {away}  {compare_score([away, home])}'

        else: text += '\n\nРезультаты последних матчей недоступны для данного матча ☹'

    elif review_type == 'h2h':

        if match_info['h2h']['avg']:

            text += "\n\nРезульты очных встреч:" \
                    f"\n\n{match_info['h2h']['order']}" \
                    f"\n\nТотал: {match_info['h2h']['total']['mut']}" \
                    f"\n\nИндивидуальный тотал:" \
                    f"\n{match_info['h2h']['total']['home']} --- {match_info['h2h']['total']['away']}"

            for title in match_info["h2h"]["avg"].keys():

                text += f'\n\n-----{title}-----' \
                        f'\n{match_info["h2h"]["avg"][title]["home"]} --- {match_info["h2h"]["avg"][title]["away"]}'

        else: text += '\n\nРезультаты очных встреч недоступны для данного матча ☹'

    elif review_type == 'fore':

        home_win = 0
        away_win = 0

        if match_info['home']['avg']: home_win += match_info['home']['win_point']['home']

        if match_info['away']['avg']: away_win += match_info['away']['win_point']['home']

        if match_info['h2h']['avg']:

            home_win += match_info['h2h']['win_point']['home']
            away_win += match_info['h2h']['win_point']['away']

        home_win += (match_info['h2h']['order'].count('✅') + match_info['home']['order'].count('✅')) * FORECAST_RATE['win']
        away_win += (match_info['h2h']['order'].count('❌') + match_info['away']['order'].count('✅')) * FORECAST_RATE['win']

        text += f'\n\nМой прогноз (POINTS: {home_win} - {away_win}):'
        if home_win > away_win: text += f"\n\nПобеда {teams[0]}"
        elif home_win < away_win: text += f"\n\nПобеда {teams[1]}"
        else: text += f"\n\nНичья"

        #if abs((home_win / away_win) - 1) < 0.1:

        home_total = 0
        away_total = 0

        if match_info['h2h']['total']:

            h2h_total = True
            home_total += match_info['h2h']['total']['home']
            away_total += match_info['h2h']['total']['away']

        if match_info['home']['total']['self'] and match_info['away']['total']['self']:

            self_total = True
            home_total += match_info['home']['total']['self']
            away_total += match_info['away']['total']['self']
        if h2h_total and self_total:

            home_total = round(home_total / 2, 1)
            away_total = round(away_total / 2, 1)

        if home_total and away_total:

            res_total = round((home_total + away_total) / 2, 1)
            text += f"\n\nСтавка на тотал (TOTAL : {res_total}):"

            if res_total < 1.5: text += "\n\nОбщий тотал меньше 1.5"
            else: text += "\n\nОбщий тотал больше 2"



    await cb.message.edit_text(text = text,
                               reply_markup = reply_markup)
