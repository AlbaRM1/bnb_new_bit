from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.requests import check_role, get_users, add_user, del_user, del_user_request, change_role
from keyboards.admin_kb import get_admin_kb
from keyboards.select_change_role import get_changerole_users
from keyboards.deleteuser_kb import get_delete_user_kb

router = Router()

@router.message(Command("admin"))
async def start_admin(message: types.Message, state: FSMContext):
    await state.clear()
    role = await check_role(message.from_user.id)
    
    if role == 'admin':
        kb = get_admin_kb()
        await message.answer(f'Выбери действие', reply_markup=kb)
        

@router.callback_query(F.data == 'view_users')
async def view_users(callback_query: types.CallbackQuery):
    users = await get_users()
    text = 'Все юзеры:\n'
    
    for i in users:
        text += f'Тэг: @{i.tg_tag} ID: {i.tg_id} Роль: {i.role}\n-------------\n'
        
    await callback_query.message.edit_text(text)
        

@router.callback_query(F.data.startswith('adduser___'))
async def add_user_tg(callback_query: types.CallbackQuery):
    print(callback_query.data)
    _, tg_id, tg_tag = callback_query.data.split('___')
    
    await add_user(tg_id, tg_tag)
    await del_user_request(tg_id)
    await callback_query.message.edit_text(f'@{tg_tag} Добавлен!')


@router.callback_query(F.data == 'change_role')
async def select_change_role(callback_query: types.CallbackQuery):    
    users = await get_users()
    kb = get_changerole_users(users)
    
    await callback_query.message.edit_text(f'Кому изменить роль?', reply_markup=kb)


@router.callback_query(F.data == 'delete_user')
async def select_del_user_tg(callback_query: types.CallbackQuery):
    users = await get_users()
    kb = get_delete_user_kb(users)
    
    await callback_query.message.edit_text(f'Выбери кого удаляем с бота', reply_markup=kb)


@router.callback_query(F.data.startswith('deluser___'))
async def del_user_tg(callback_query: types.CallbackQuery):
    _, tg_id, tg_tag = callback_query.data.split('___')
    
    await del_user(tg_id)
    await callback_query.message.edit_text(f'@{tg_tag} Уволен!')
    
@router.callback_query(F.data.startswith('changerole___'))
async def change_role_tg(callback_query: types.CallbackQuery):
    _, tg_id, role= callback_query.data.split('___')
    
    if role == 'user':
        role = 'admin'
    else:
        role = 'user'
        
    await change_role(tg_id, role)
    await callback_query.message.edit_text(f'Изменено на {role}')