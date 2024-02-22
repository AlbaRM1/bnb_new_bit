from aiogram import types

def get_delete_user_kb(users):
    buttons = [
    ]
    
    for user in users:
        buttons.append([types.InlineKeyboardButton(text=f"@{user.tg_tag}", callback_data=f"deluser___{user.tg_id}___{user.tg_tag}")])
        
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard