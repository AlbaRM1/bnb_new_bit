from aiogram import types

def get_clear_statistic_kb():
    buttons = [
    ]
    
    buttons.append([types.InlineKeyboardButton(text=f"Очистить всю статистику", callback_data=f"clear_statistic")])
        
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard