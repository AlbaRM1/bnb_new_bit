from aiogram import types

def get_changerole_users(users):
    buttons = []
    for user in users:
        buttons.append([types.InlineKeyboardButton(text=f"@{user.tg_tag}: {user.role}", callback_data=f"changerole___{user.tg_id}___{user.role}")])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard