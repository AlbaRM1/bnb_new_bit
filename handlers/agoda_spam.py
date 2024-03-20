import traceback
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.state import State, StatesGroup

from utils import check_proxy, create_link_agota, replace_template
from models.agoda import AgodaAccount

from keyboards.users.proxy_kb import get_proxy_kb
from keyboards.users.domainids_kb import get_domainids_kb
from database.requests import get_proxies, get_domains_id, add_count_success_send_bnb, add_count_success_send_messages_bnb

from .book_spam import bot

router = Router()
router.message.filter(
    F.chat.type == "private"
)


class DataAdoga(StatesGroup):
    proxy = State()
    cookie_filepath = State()
    domain_id = State()
    text_message = State()
    ready = State()


async def update_mess(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    count_all = data['count_all']
    count_sented = data['count']
    await message.edit_text(f'Сообщения отправлены {count_sented}/{count_all} юзерам. (Обновляется каждые 10 сек.)')


@router.callback_query(F.data == 'start_send_adoga')
async def get_hotel_id(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer('OK')
    message = callback_query.message
    
    proxies = await get_proxies(callback_query.from_user.id)
    kb = get_proxy_kb(proxies)
    
    await message.answer('Скинь мне прокси формата: login:password@ip:port (socks5 с авторизацией) или http (ip:port)', reply_markup=kb)
    await state.set_state(DataAdoga.proxy)

@router.message(DataAdoga.proxy, F.text)
async def get_proxy(message: types.Message, state: FSMContext):
    await message.answer('Проверка подключения по прокси')
    proxy = message.text
    response = await check_proxy.check(proxy)

    if response:
        await message.answer(f'Ip твоей прокси: {response}')
        await message.answer(f'Скинь куки (json/netscape)')
        await state.update_data(proxy=proxy)
        await state.set_state(DataAdoga.cookie_filepath)
    else:
        await message.answer('Не удалось подключиться к прокси, перезапусти бота и попробуй снова')


@router.message(DataAdoga.cookie_filepath, F.document)
async def get_and_check_cookie(message: types.Message, state: FSMContext):
    await message.answer('Идёт проверка акка, подожди чуток')
    cookie_path = f'./tmp/cookies/{message.document.file_id}.json'
    proxy = await state.get_data()
    proxy = proxy['proxy']
    
    await bot.download(message.document,
                       destination=cookie_path)
    await state.update_data(cookie_filepath=cookie_path)
    
    account = AgodaAccount(cookie_file=cookie_path, proxy=proxy)
    test_cookie = await account.check_cookies()
    
    if test_cookie:
        domains_id = await get_domains_id(message.from_user.id)
        kb = get_domainids_kb(domains_id)
        
        await message.answer('В акк зашли. Теперь отправь мне domain id', reply_markup=kb)
        await state.update_data(account_model=account)
        
        await state.set_state(DataAdoga.domain_id)
    else:
        await message.answer('В акк не зашли. Отправь другие куки')
        await state.set_state(DataAdoga.cookie_filepath)


@router.message(DataAdoga.domain_id, F.text)
async def get_domain_id(message: types.Message, state: FSMContext):
    domain_id = message.text
    
    await message.answer('Теперь отправь мне сообщение для мамонтов и мы начнём работу!')
    await state.update_data(domain_id=domain_id)
    await state.set_state(DataAdoga.text_message)
    

@router.message(DataAdoga.text_message, F.text)
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
        await message.answer('Не удалось получить брони, скинь другие куки')
        await state.set_state(DataAdoga.cookie_filepath)
        return 0
    await message.answer(f'Спарсили {len(reservations)} броней')
    if len(reservations) == 0:
        await message.answer('Cкинь другие куки')
        await state.set_state(DataAdoga.cookie_filepath)
    else:
        await message.answer('✅ Создаём ссылки! ✅')
        try:
            for reservation in reservations:
                print(reservation)
                hotel_name = reservation['hotel_name']
                full_name = reservation['name']
                
                url = await create_link_agota.create_link_agota(chat_id=message.from_user.id,
                                            price=reservation['price'],
                                            image_url=reservation['hotel_image'],
                                            room_name=hotel_name,
                                            address=reservation['hotel_address'],
                                            date_start=reservation['checkin'],
                                            date_end=reservation['checkout'],
                                            domain_id=domain_id,
                                            mamont_name=full_name
                                            )
                
                ready_data.append({'hotel_name': hotel_name,
                                   'checkIn': reservation['checkin'],
                                   'checkOut': reservation['checkout'],
                                   'full_name': full_name, 
                                   'url': url, 
                                   'bookingId': reservation['bookingId'],
                                   'memberId': reservation['memberId'],
                                   'conversation_id': reservation['conversation_id']
                                   })
            await message.answer('✅ Ссылки созданы! Напиши любое сообщение, чтобы продолжить ✅')
        except Exception as err:
            print(traceback.format_exc())
            await message.answer('Не удалось создать ссылки (возможно указан не верный domain id), скинь другие куки')
            await state.set_state(DataAdoga.cookie_filepath)
            return 0

        await state.update_data(reservations=ready_data)
        await state.set_state(DataAdoga.ready)


@router.message(DataAdoga.ready, F.text)
async def send(message: types.Message, state: FSMContext):
    mess = await message.answer('✅ Шлём! ✅')
    
    state_data = await state.get_data()
    ready_data = state_data['reservations']
    account_model = state_data['account_model']
    text_message = state_data['text_message']

    count_reservations = len(ready_data)
    count_sented = 0
    
    mess = await message.answer(f'Сообщения отправлены {count_sented}/{count_reservations} юзерам. (Обновляется каждые 10 сек.)')
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_mess, 'interval', args=[mess, state], seconds=10)
    scheduler.start()
    
    await state.update_data(count_all=count_reservations)
    await state.update_data(count=count_sented)
    for data in ready_data:
        text = replace_template.replcate_in_text(text_message, data['full_name'], data['hotel_name'], data['url'])
        result = await account_model.send_message(text, data['conversation_id'], data['memberId'], data['bookingId'], data['checkIn'], data['checkOut'], data['full_name'], data['hotel_name'])
        
        if result:
            count_sented += 1
            # await add_count_success_send_messages_bnb(message.from_user.id)

        await state.update_data(count=count_sented)
        # await mess.edit_text(f'Отправили {count_sented}/{count_reservations} сообщений')

    scheduler.shutdown()
    await message.answer(f'✅ {count_sented}/{count_reservations} сообщений отправлено ✅')
    # await add_count_success_send_bnb(message.from_user.id)
    await state.clear()
    