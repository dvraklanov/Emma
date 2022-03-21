from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import VK_LINK

"""Кнопка с ссылкой на группу ВК"""
vk_btn = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = "ВКонтакте", url = VK_LINK)]])
