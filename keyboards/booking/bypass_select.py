from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_bypass_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Да", callback_data="use_bypass"),
            types.InlineKeyboardButton(text="Нет", callback_data="not_bypass")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard