import traceback
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from utils import check_proxy, create_links, replace_template
from models.airbnb import AirbnbAccount

from keyboards.users.proxy_kb import get_proxy_kb
from keyboards.users.domainids_kb import get_domainids_kb
from keyboards.users.text_kb import get_texts_kb
from database.requests import get_proxies, get_domains_id, get_texts

from .start import Data, bot

router = Router()
router.message.filter(
    F.chat.type == "private"
)


@router.callback_query(F.data == 'start_send')
async def get_hotel_id(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer('OK')
    message = callback_query.message
    
    proxies = await get_proxies(callback_query.from_user.id)
    kb = get_proxy_kb(proxies)
    
    await message.answer('Скинь мне прокси формата: login:password@ip:port (socks5 с авторизацией)', reply_markup=kb)
    await state.set_state(Data.proxy)

@router.message(Data.proxy, F.text)
async def get_proxy(message: types.Message, state: FSMContext):
    await message.answer('Проверка подключения по прокси')
    proxy = message.text
    response = await check_proxy.check(proxy)

    if response:
        await message.answer(f'Ip твоей прокси: {response}')
        await message.answer(f'Скинь куки (json/netscape)')
        await state.update_data(proxy=proxy)
        await state.set_state(Data.cookie_filepath)
    else:
        await message.answer('Не удалось подключиться к прокси, перезапусти бота и попробуй снова')


@router.message(Data.cookie_filepath, F.document)
async def get_and_check_cookie(message: types.Message, state: FSMContext):
    await message.answer('Идёт проверка акка, подожди чуток')
    cookie_path = f'./tmp/cookies/{message.document.file_id}.json'
    proxy = await state.get_data()
    proxy = proxy['proxy']
    
    await bot.download(message.document,
                       destination=cookie_path)
    await state.update_data(cookie_filepath=cookie_path)
    
    account = AirbnbAccount(cookie_file=cookie_path, proxy=proxy)
    test_cookie = await account.check_cookies()
    
    if test_cookie:
        domains_id = await get_domains_id(message.from_user.id)
        kb = get_domainids_kb(domains_id)
        
        await message.answer('В акк зашли. Теперь отправь мне domain id', reply_markup=kb)
        await state.update_data(account_model=account)
        
        await state.set_state(Data.domain_id)
    else:
        await message.answer('В акк не зашли. Отправь другие куки')
        await state.set_state(Data.cookie_filepath)


@router.message(Data.domain_id, F.text)
async def get_domain_id(message: types.Message, state: FSMContext):
    domain_id = message.text
    
    texts = await get_texts(message.from_user.id)
    kb = get_texts_kb(texts)
    
    await message.answer('Теперь отправь мне сообщение для мамонтов и мы начнём работу!', reply_markup=kb)
    await state.update_data(domain_id=domain_id)
    await state.set_state(Data.text_message)
    

@router.message(Data.text_message, F.text)
async def get_text_message(message: types.Message, state: FSMContext):
    ready_data = []
    
    text_message = message.text
    await state.update_data(text_message=text_message)
    
    state_data = await state.get_data()
    account_model = state_data['account_model']
    domain_id = state_data['domain_id']
    
    await message.answer('✅ Получаем брони ✅')
    try:
        reservations = await account_model.get_reservations()
    
    except Exception as err:
        print(traceback.format_exc())
        await message.answer('Не удалось получить брони (скорее всего валюты нет в списке, напиши админам), скинь другие куки')
        await state.set_state(Data.cookie_filepath)
        return 0
    await message.answer(f'Спарсили {len(reservations)} броней')
    await message.answer('✅ Создаём ссылки! ✅')
    try:
        for reservation in reservations:
            reserv_code = reservation['reserv_code']
            hotel_name = reservation['hotel_name']
            full_name = reservation['full_name']
            thread_token = reservation['thread_token']
            
            url = await create_links.create_link(chat_id=message.from_user.id,
                                        price=reservation['total'],
                                        image_url=reservation['hotel_image'],
                                        room_name=hotel_name,
                                        address=reservation['address'],
                                        date_start=reservation['start_date'],
                                        date_end=reservation['end_date'],
                                        domain_id=domain_id
                                        )
            
            ready_data.append({'reserv_code': reserv_code, 'hotel_name': hotel_name, 'full_name': full_name, 'url': url, 'thread_token': thread_token})
        await message.answer('✅ Ссылки созданы! Напиши любое сообщение, чтобы продолжить ✅')
    except Exception as err:
        print(traceback.format_exc())
        await message.answer('Не удалось создать ссылки (возможно указан не верный domain id), скинь другие куки')
        await state.set_state(Data.cookie_filepath)
        return 0

    await state.update_data(reservations=ready_data)
    await state.set_state(Data.ready)


@router.message(Data.ready, F.text)
async def send(message: types.Message, state: FSMContext):
    mess = await message.answer('✅ Шлём! ✅')
    
    state_data = await state.get_data()
    ready_data = state_data['reservations']
    account_model = state_data['account_model']
    text_message = state_data['text_message']

    count_reservations = len(ready_data)
    count_sented = 0
    
    for data in ready_data:
        text = replace_template.replcate_in_text(text_message, data['full_name'], data['hotel_name'], data['url'])
        result = await account_model.send_message(text, data['reserv_code'], data['thread_token'])
        
        if result:
            count_sented += 1
        
        # await mess.edit_text(f'Отправили {count_sented}/{count_reservations} сообщений')
            
    await message.answer(f'✅ {count_sented}/{count_reservations} сообщений отправлено ✅')
    await state.clear()
    