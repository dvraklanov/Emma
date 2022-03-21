from aiogram.utils.callback_data import CallbackData

"""Callback для inline - кнопок"""

sport_cb = CallbackData("m", "sport") #Callback для меню выбора спорта
date_cb = CallbackData("m", "sport", "date") #Callback для меню выбора даты
champ_cb = CallbackData("m", "sport", "date", "champ_id") #Callback для меню выбора чемпионата
match_cb = CallbackData("m", "sport", "date", "champ_id", "match_id", "match_num", "review_type") #Callback для меню выбора матча