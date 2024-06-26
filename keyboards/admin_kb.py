from aiogram import types

def get_admin_kb():
    buttons = [
        [types.InlineKeyboardButton(text="Посмотреть список юзеров", callback_data="view_users")],
        [types.InlineKeyboardButton(text="Посмотреть статистику юзеров", callback_data="view_statistics")],
        [types.InlineKeyboardButton(text="Отобрать доступ к боту", callback_data="delete_user")],
        [types.InlineKeyboardButton(text="Изменить роль юзеру", callback_data="change_role")],
        [types.InlineKeyboardButton(text="Отправить сообщение всем юзерам", callback_data="send_all_message")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard