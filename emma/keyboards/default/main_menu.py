from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

schedule_txt = "📅Расписание📅"
about_txt = "❔Обо мне❔"

main_menu = ReplyKeyboardMarkup(keyboard = [
                                [KeyboardButton(text = schedule_txt)],
                                [KeyboardButton(text = about_txt)]
                                ], resize_keyboard = True)