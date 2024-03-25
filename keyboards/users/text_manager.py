from aiogram import types

def get_text_manager_kb(text_id):
    kb = []
    
    kb.append([types.InlineKeyboardButton(text='Редактировать', callback_data=f'edit_text___{text_id}')])
    kb.append([types.InlineKeyboardButton(text='Удалить', callback_data=f'delete_text___{text_id}')])

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb, resize_keyboard=True)
    return keyboard