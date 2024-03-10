from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app import bot, chat_id, scheduler
from utils import check_proxy, create_links, replace_template
from models.airbnb import AirbnbAccount

from database.requests import get_user,\
                            check_user,\
                            add_request_user,\
                            get_domains_id,\
                            add_domains_id,\
                            del_domains_id,\
                            get_proxies,\
                            add_proxy,\
                            del_proxy,\
                            get_texts,\
                            add_text,\
                            del_text, change_role
                            
from keyboards.request_kb import get_request_kb
from keyboards.adduser_kb import get_adduser_kb

from keyboards.users.home import get_home_kb, view_domains_id, view_proxies, view_texts

router = Router()
router.message.filter(
    F.chat.type == "private"
)


class Data(StatesGroup):
    test = State()
    cookie_filepath = State()
    account_model = State()
    domain_id = State()
    proxy = State()
    text_message = State()
    reservations = State()
    ready = State()
    
    domain_id_add = State()
    proxy_add = State()
    text_message_add = State()
    
    count_all = State()
    count = State()


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    result_check = await check_user(int(message.from_user.id))
    status = result_check['status']
    print(message.from_user.username)
    # await change_role(message.from_user.id, 'admin')

    if status == 'ok':
        user = await get_user(message.from_user.id)
        kb = get_home_kb(user)
        
        await message.answer('Привет! давай начнём работу? ', reply_markup=kb)
    elif status == 'request':
        await message.answer('Ты уже подал заявку, подожди пока админы её примут')
    else:
        kb = get_request_kb()
        await message.answer('Доступа нет :(', reply_markup=kb)


@router.callback_query(F.data == 'send_request')
async def send_request(callback_query: types.CallbackQuery):
    kb = get_adduser_kb(callback_query.from_user.id, callback_query.from_user.username)
    
    await add_request_user(tg_id=callback_query.from_user.id,
                           tg_tag=callback_query.from_user.username
                           )
    
    await callback_query.message.edit_text('Заявка отправлена. Ожидай!')
    await bot.send_message(chat_id=chat_id, 
                           text=f'@{callback_query.from_user.username} Отправил заявку на получение доступа к боту', 
                           reply_markup=kb
                           )


@router.callback_query(F.data == 'view_domainids')
async def view_domainids(callback_query: types.CallbackQuery):
    domain_ids = await get_domains_id(callback_query.from_user.id)
    domain_ids_kb = view_domains_id(domain_ids)
    
    await callback_query.message.edit_text('Выбери домен (при нажатии удалится из сохранённых)', reply_markup=domain_ids_kb)

@router.callback_query(F.data == 'add_domainid')
async def add_domainid(callback_query: types.CallbackQuery, state: FSMContext):    
    await callback_query.message.edit_text('Напиши domain id для сохранения')
    await state.set_state(Data.domain_id_add)

@router.callback_query(F.data.startswith('actiondomain___'))
async def delete_domainid(callback_query: types.CallbackQuery, state: FSMContext):
    _, id_domain = callback_query.data.split('___')
    await del_domains_id(id_domain)
    
    await callback_query.message.edit_text(f'domain id удалён')

@router.message(Data.domain_id_add, F.text)
async def get_domain_id(message: types.Message, state: FSMContext):
    await add_domains_id(message.from_user.id, message.text)
    user = await get_user(message.from_user.id)
    kb = get_home_kb(user)
    
    await message.answer('Домен успешно добавлен', reply_markup=kb)
    await state.clear()



@router.callback_query(F.data == 'view_texts')
async def view_texts_home(callback_query: types.CallbackQuery):
    text = await get_texts(callback_query.from_user.id)
    text_kb = view_texts(text)
    
    await callback_query.message.edit_text('Выбери текст (при нажатии удалится из сохранённых)', reply_markup=text_kb)
    
@router.callback_query(F.data == 'add_text')
async def add_text_tg(callback_query: types.CallbackQuery, state: FSMContext):    
    await callback_query.message.edit_text('Напиши текст для сохранения')
    await state.set_state(Data.text_message_add)

@router.callback_query(F.data.startswith('actiontext___'))
async def delete_text_tg(callback_query: types.CallbackQuery, state: FSMContext):
    _, text = callback_query.data.split('___')
    await del_text(text)
    
    await callback_query.message.edit_text(f'Текст удалён')

@router.message(Data.text_message_add, F.text)
async def get_text_tg(message: types.Message, state: FSMContext):
    await add_text(message.from_user.id, message.text)
    user = await get_user(message.from_user.id)
    kb = get_home_kb(user)
    
    await message.answer('Текст успешно добавлен', reply_markup=kb)
    await state.clear()


@router.callback_query(F.data == 'view_proxies')
async def view_proxy_home(callback_query: types.CallbackQuery):
    proxies = await get_proxies(callback_query.from_user.id)
    proxies_kb = view_proxies(proxies)
    
    await callback_query.message.edit_text('Выбери прокси (при нажатии удалится из сохранённых)', reply_markup=proxies_kb)
    
@router.callback_query(F.data == 'add_proxy')
async def add_proxy_tg(callback_query: types.CallbackQuery, state: FSMContext):    
    await callback_query.message.edit_text('Напиши прокси для сохранения')
    await state.set_state(Data.proxy_add)

@router.callback_query(F.data.startswith('actionproxy___'))
async def delete_proxy_tg(callback_query: types.CallbackQuery, state: FSMContext):
    _, proxy = callback_query.data.split('___')
    await del_proxy(proxy)
    
    await callback_query.message.edit_text(f'Прокси удалён')

@router.message(Data.proxy_add, F.text)
async def get_proxy_tg(message: types.Message, state: FSMContext):
    await add_proxy(message.from_user.id, message.text)
    
    user = await get_user(message.from_user.id)
    kb = get_home_kb(user)
    
    await message.answer('Прокси успешно добавлен', reply_markup=kb)
    await state.clear()
