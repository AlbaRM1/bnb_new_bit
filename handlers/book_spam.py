from asyncio import sleep
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards.users.domainids_kb import get_domainids_kb
from models.booking import BookingAccount
from keyboards.users.proxy_kb import get_proxy_kb
from keyboards.booking.select_hotel_id import get_hostels_keyboard
from database.requests import get_domains_id, get_proxies
from utils.replace_template import replcate_in_text
from utils.create_links import create_link
from utils import check_proxy
from database.requests import add_count_success_send_book, add_count_success_send_messages_book

# from app import scheduler
from .admin_panel import bot

class DataBooking(StatesGroup):
    cookie_filepath = State()
    account_model = State()
    domain_id = State()
    proxy = State()
    pia_proxy_port = State()
    proxy_type = State()
    message_text = State()
    ready = State()
    ready_data = State()
    hotel_id = State()
    
    count_all = State()
    count = State()

    
router = Router()


async def update_mess(message: types.Message, state: FSMContext):
    data = await state.get_data()
    count_all = data['count_all']
    count_sented = data['count']
    await message.edit_text(f'Сообщения отправлены {count_sented}/{count_all} юзерам. (Обновляется каждые 10 сек.)')


@router.callback_query(F.data == 'start_send_book_socks')
async def get_hotel_id(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer('OK')
    message = callback_query.message
    
    proxies = await get_proxies(callback_query.from_user.id)
    kb = get_proxy_kb(proxies)
    
    await message.answer('Скинь мне прокси формата: login:password@ip:port (socks5 с авторизацией) или http (ip:port)', reply_markup=kb)
    await state.set_state(DataBooking.proxy)
    await state.update_data(proxy_type='socks')


@router.callback_query(F.data == 'start_send_book_pia')
async def select_port(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer('OK')
    await callback_query.message.answer('Скинь порт прокси. (Попроси у @waaleb)')

    await state.set_state(DataBooking.pia_proxy_port)

@router.message(DataBooking.pia_proxy_port)
async def check_proxy_pia(message: types.Message, state: FSMContext):
    port = message.text
    await message.answer('Проверка подключения по прокси')
    
    response = await check_proxy.check(f'127.0.0.1:{port}')
    if response:
        await message.answer(f'Ip твоей прокси: {response}')
        await message.answer(f'Скинь куки (json/netscape)')
        await state.update_data(proxy_type='pia')
        await state.update_data(proxy=f'127.0.0.1:{port}')
        await state.set_state(DataBooking.cookie_filepath)
    else:
        await message.answer('Не удалось подключиться к прокси, напиши @waaleb, он подрубит прокси')

@router.message(DataBooking.proxy, F.text)
async def get_proxy(message: types.Message, state: FSMContext):
    await message.answer('Проверка подключения по прокси')
    proxy = message.text
    proxy = proxy.replace('socks5://', '')
    response = await check_proxy.check(proxy)

    if response:
        await message.answer(f'Ip твоей прокси: {response}')
        await message.answer(f'Скинь куки (json/netscape)')
        await state.update_data(proxy=proxy)
        await state.set_state(DataBooking.cookie_filepath)
    else:
        await message.answer('Не удалось подключиться к прокси, скинь другие прокси')
        await state.set_state(DataBooking.proxy)

@router.message(DataBooking.cookie_filepath, F.document)
async def get_and_check_cookie(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    await message.answer('Идёт проверка акка, подожди чуток')
    cookie_path = f'./tmp/cookies/{message.document.file_id}.json'
    proxy = await state.get_data()
    proxy = proxy['proxy']
    
    await bot.download(message.document,
                       destination=cookie_path)
    await state.update_data(cookie_filepath=cookie_path)
    
    account = BookingAccount(cookie_file=cookie_path, proxy=proxy, type_proxy=data['proxy_type'])
    test_cookie = await account.check_cookies()
    
    domains_id = await get_domains_id(message.from_user.id)
    kb = get_domainids_kb(domainids=domains_id)
    
    await state.update_data(account_model=account)
    
    if test_cookie['status']:
        await state.update_data(hotel_name=test_cookie['hotel_name'])

        await message.answer('✅')
        await message.answer('Отлично, мы зашли в акк, можем начать работу!')
        await message.answer('А теперь скинь мне domain id', reply_markup=kb)
        
        await state.set_state(DataBooking.domain_id)
    else:
        await message.answer('❌')
        await message.answer('Войти в акк не получилось, попробуй скинуть другие куки')
        await state.set_state(DataBooking.cookie_filepath)


@router.message(DataBooking.domain_id, F.text)
async def get_domain_id(message: types.Message, state: FSMContext):
    domain_id = message.text
    
    await message.answer('Теперь отправь мне сообщение для мамонтов и мы начнём работу!')
    await state.update_data(domain_id=domain_id)
    await state.set_state(DataBooking.message_text)
    
    
@router.message(DataBooking.message_text, F.text)
async def get_domain(message: types.Message, state: FSMContext):    
    data = await state.get_data()
    message_text = message.text
    
    print(data)
    
    account_model = data['account_model']
    domain_id = data['domain_id']
    
    
    await message.answer(f'Парсим брони! Подожди чутка')
    reservations = await account_model.get_reservations()
    if reservations:
        print(reservations)
        await message.answer(f'Спарсили {len(reservations)} броней!')
        ready_data = []
        
        await message.answer(f'Создаём ссылки!')
        if len(reservations) == 0:
            await message.answer('Cкинь другие куки')
            await state.set_state(DataBooking.cookie_filepath)
        else:
            for reserv in reservations:
                link = await create_link(message.from_user.id,
                                        reserv['price'],
                                        reserv['image'],
                                        reserv['room_name'],
                                        reserv['address'],
                                        reserv['date_start'],
                                        reserv['date_end'],
                                        domain_id
                                        )
                
                ready_data.append({
                    'id': reserv['id_guest'],
                    'link': link,
                    'name': reserv['name'],
                    'hotel_name': reserv['hotel_name'],
                    'hotel_id': reserv['hotel_id']
                })
            await message.answer(f'Ссылки созданы!')
            await message.answer(f'Для продолжения введи любое сообщение')
            await state.set_state(DataBooking.ready)
            await state.update_data(ready_data=ready_data)
            await state.update_data(message_text=message_text)
    else:
        await message.answer('Получить брони не удалось')
    

@router.message(DataBooking.ready, F.text)
async def send_message(message: types.Message, state: FSMContext):
    await message.answer('✅')
    await message.answer('Отправляем сообщения мамонтам!')
    
    data = await state.get_data()
    
    ready_data = data['ready_data']
    account_model = data['account_model']
    hotel_name = data['hotel_name']
    message_text = data['message_text']
    
    sentet_messages = 0
    count_messages = len(ready_data)
    
    scheduler = AsyncIOScheduler()
    mess = await message.answer(f'Сообщения отправлены {sentet_messages}/{count_messages} юзерам. (Обновляется каждые 10 сек.)')
    
    scheduler.add_job(update_mess, 'interval', args=[mess, state], seconds=10)
    scheduler.start()
    
    await state.update_data(count_all=count_messages)
    await state.update_data(count=sentet_messages)
    for i in ready_data:
        text = replcate_in_text(message_text, i['name'], i['hotel_name'], i['link'])
        id_reserv = i['id']
        hotel_id = i['hotel_id']
        
        result = await account_model.send_messages(text, id_reserv, hotel_id)
        if result['status']:
            sentet_messages += 1
            await add_count_success_send_messages_book(message.from_user.id)
        elif not result['status'] and result['reason'] == 'not_in_account':
            await message.answer(f'Выкинуло с аккаунта :(, Попробуй ещё раз (ошибка 401)')
            scheduler.shutdown()
            await state.clear()
            return 0
        elif not result['status'] and result['reason'] == 'edit_proxy':
            await message.answer(f'Сообщение не отправилось, поменяй прокси (ошибка 403)')
            scheduler.shutdown()
            await state.clear()
            return 0
            
        await state.update_data(count=sentet_messages)

    scheduler.shutdown()
    await message.answer(f'''{hotel_name}
✅ Рассылка завершена! ✅
🟢 Текущая статистика: ({sentet_messages}/{count_messages})''')
    await add_count_success_send_book(message.from_user.id)
    await state.clear()
