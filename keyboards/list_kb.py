from aiogram import types

def get_list_kb(next_int):
    preverious = next_int - 10
    next_list = next_int + 10
    
    buttons = []
    print(preverious)
    if preverious > 0:
        buttons.append([types.InlineKeyboardButton(text='<-', callback_data=f'list__pre__{preverious}')])
        
    buttons.append([types.InlineKeyboardButton(text='->', callback_data=f'list__next__{next_list}')])
    buttons.append([types.InlineKeyboardButton(text=f"Очистить всю статистику", callback_data=f"clear_statistic")])
    
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard