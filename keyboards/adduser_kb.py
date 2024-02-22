from aiogram import types

def get_adduser_kb(tg_id: int, tg_tag):
    buttons = [
        [
            types.InlineKeyboardButton(text="Принять", callback_data=f"adduser___{tg_id}___{tg_tag}"),
            types.InlineKeyboardButton(text="Отклонить", callback_data=f"declineuser___{tg_id}"),
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard