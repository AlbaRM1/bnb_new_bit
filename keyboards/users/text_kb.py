from aiogram import types

def get_texts_kb(texts):
    kb = []
    
    if texts:
        for text in texts:
            kb.append([types.KeyboardButton(text=str(text.text))])

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard