from aiogram import types

def get_request_kb():
    buttons = [
        [
            types.InlineKeyboardButton(text="Отправить заявку на получение доступа", callback_data="send_request"),
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard