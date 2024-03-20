from aiogram import types

def get_home_kb(user):
    buttons = [
            [types.InlineKeyboardButton(text="Разослать сообщения AIRBNB", callback_data="start_send")],
            [types.InlineKeyboardButton(text="Разослать сообщения BOOKING (pia. Ждать админов)", callback_data="start_send_book_pia")],
            [types.InlineKeyboardButton(text="Разослать сообщения BOOKING (socks. Сразу слать)", callback_data="start_send_book_socks")],
            [types.InlineKeyboardButton(text="Разослать сообщения AGODA (socks. Сразу слать)", callback_data="start_send_adoga")],
            # [types.InlineKeyboardButton(text="Разослать сообщения BOOKING (pulse. Прокси не нужны)", callback_data="start_send_book_pulse")],
            [types.InlineKeyboardButton(text="Просмотреть сохранённые domain id", callback_data="view_domainids")],
            [types.InlineKeyboardButton(text="Просмотреть сохранённые прокси", callback_data="view_proxies")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def view_domains_id(domains):
    buttons = [
    ]
    
    if domains:
        for domain_id in domains:
            buttons.append([types.InlineKeyboardButton(text=str(domain_id.domain_id), callback_data=f'actiondomain___{domain_id.id}')])

    buttons.append([types.InlineKeyboardButton(text='Добавить domain id', callback_data='add_domainid')])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def view_texts(texts):
    buttons = [
    ]
    
    if texts:
        for text in texts:
            buttons.append([types.InlineKeyboardButton(text=str(text.text), callback_data=f'actiontext___{text.id}')])
            
    buttons.append([types.InlineKeyboardButton(text='Добавить текст', callback_data='add_text')])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def view_proxies(proxies):
    buttons = [
    ]
    
    if proxies:
        for proxy in proxies:
            buttons.append([types.InlineKeyboardButton(text=str(proxy.proxy), callback_data=f'actionproxy___{proxy.id}')])
    
    buttons.append([types.InlineKeyboardButton(text='Добавить прокси', callback_data='add_proxy')])
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


