from aiogram import types

def get_proxy_kb(proxies):
    kb = []
    
    if proxies:
        for proxy in proxies:
            kb.append([types.KeyboardButton(text=str(proxy.proxy))])

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard