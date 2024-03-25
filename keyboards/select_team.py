from aiogram import types

def get_team_kb():
    buttons = []
    buttons.append([types.InlineKeyboardButton(text=f'TOP', callback_data='select___top')])
    buttons.append([types.InlineKeyboardButton(text=f'WOZA', callback_data='select___default')])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard