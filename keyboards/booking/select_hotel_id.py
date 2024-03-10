from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_hostels_keyboard(hostels):
    builder = InlineKeyboardBuilder()
    for i in hostels:
        i = i
        
        builder.add(
            types.InlineKeyboardButton(
                text=f'{i[0:21]}',
                callback_data=f'{i[0:21]}'
            )
        )
    
    return builder.as_markup()