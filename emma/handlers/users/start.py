from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from keyboards.default import main_menu

welcome_txt = \
"""Привет, {user}, меня зовут Эмма!
Я твой личный помощник в сфере аналитики спортивных событий.
Я предоставлю тебе самую важную информацию о матче и помогу принять правильное решение! """

#Приветсвие бота
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(welcome_txt.format(user = message.from_user.full_name),
                         reply_markup = main_menu)
