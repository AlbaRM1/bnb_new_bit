from aiogram import types

def get_domainids_kb(domainids):
    kb = []
    
    if domainids:
        for domainid in domainids:
            kb.append([types.KeyboardButton(text=str(domainid.domain_id))])

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard