from sqlalchemy.orm import selectinload
from database.models import User, DomainId, Proxy, Text, UserRequest, async_session
from sqlalchemy import select

async def get_users():
    async with async_session() as session:
        result = await session.scalars(select(User))
        return result
    

async def get_user(tg_id):
    async with async_session() as session:
        result = await session.scalar(select(User).filter_by(tg_id=tg_id))
        return result


async def add_user(tg_id: int, tg_tag: str):
    async with async_session() as session:
        user = User(tg_id=tg_id, tg_tag=tg_tag)
        session.add(user)
        await session.commit()
        
        return True

async def check_user(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).filter_by(tg_id=tg_id))
        
        if not result:
            result = await session.scalar(select(UserRequest).filter_by(tg_id=tg_id))
            if not result:
                return {'result': None, 'status': 'none'}
            
            return {'result': result, 'status': 'request'}
        return {'result': result, 'status': 'ok'}

async def add_request_user(tg_id: int, tg_tag: str):
    async with async_session() as session:
        user = UserRequest(tg_id=tg_id, tg_tag=tg_tag)
        session.add(user)
        await session.commit()
        
        return True

async def check_role(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).filter_by(tg_id=tg_id))
        return result.role


async def del_user(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).filter_by(tg_id=tg_id))
        
        domains_id = await get_domains_id(tg_id)
        proxies = await get_proxies(tg_id)
        texts = await get_texts(tg_id)
        
        print(domains_id, proxies, texts)
        
        if domains_id:
            await session.delete(domains_id[0])
        if proxies:
            await session.delete(proxies[0])
        if texts:
            await session.delete(texts[0])
        await session.delete(result)
        await session.commit()
        return True
    

async def del_user_request(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(UserRequest).filter_by(tg_id=tg_id))
        
        await session.delete(result)
        await session.commit()
        return True

    
async def change_role(tg_id: int, role: str):
    async with async_session() as session:
        result = await session.scalar(select(User).filter_by(tg_id=tg_id))
        result.role = role
        
        session.add(result)
        await session.commit()
        return True
    

async def get_domains_id(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).options(selectinload(User.domain_ids)).filter_by(tg_id=tg_id))
        result = result.domain_ids
        
        return result 


async def add_domains_id(tg_id: int, domain_id: str):
    async with async_session() as session:
        result = await session.scalar(select(User).options(selectinload(User.domain_ids)).filter_by(tg_id=tg_id))
        result.domain_ids.append(DomainId(domain_id=domain_id))
        
        session.add(result)
        await session.commit()
        return True    


async def del_domains_id(domain_id: int):
    async with async_session() as session:
        result = await session.scalar(select(DomainId).filter_by(id=domain_id))
        
        await session.delete(result)
        await session.commit()
        return True 

async def get_proxies(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).options(selectinload(User.proxies)).filter_by(tg_id=tg_id))
        result = result.proxies
        
        return result 


async def add_proxy(tg_id: int, proxy: str):
    async with async_session() as session:
        result = await session.scalar(select(User).options(selectinload(User.proxies)).filter_by(tg_id=tg_id))
        result.proxies.append(Proxy(proxy=proxy))
        
        session.add(result)
        await session.commit()
        return True
    
    
async def del_proxy(proxy_id: int):
    async with async_session() as session:
        result = await session.scalar(select(Proxy).filter_by(id=proxy_id))
        
        await session.delete(result)
        await session.commit()
        return True 


async def get_texts(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).options(selectinload(User.texts)).filter_by(tg_id=tg_id))
        result = result.texts
        
        return result


async def get_text(text_id: int):
    async with async_session() as session:
        result = await session.scalar(select(Text).filter_by(id=text_id))
        result = result.text
        
        return result 
    


async def get_text_for_name(text_name: str, tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).options(selectinload(User.texts)).filter_by(tg_id=tg_id))
        result = result.texts
        
        for i in result:
            if i.name == text_name:
                return i.text
        return False


async def add_text(tg_id: int, name: str, text: str):
    async with async_session() as session:
        result = await session.scalar(select(User).options(selectinload(User.texts)).filter_by(tg_id=tg_id))
        result.texts.append(Text(name=name, text=text))
        
        session.add(result)
        await session.commit()
        return True
    

async def del_text(text_id: int):
    async with async_session() as session:
        result = await session.scalar(select(Text).filter_by(id=text_id))
        
        await session.delete(result)
        await session.commit()
        return True


async def edit_text_req(text_id: int, text: str):
    async with async_session() as session:
        result = await session.scalar(select(Text).filter_by(id=text_id))
        result.text = text
        
        await session.commit()
        return True


async def get_all_statistic():
    async with async_session() as session:
        data = []
        
        result = await session.scalars(select(User))
        for i in result:
            data.append(
                    {'user': i.tg_tag, 
                    'count_success_send_book': i.count_success_send_book,
                    'count_success_send_bnb': i.count_success_send_bnb,
                    'count_success_send_messages_book': i.count_success_send_messages_book,
                    'count_success_send_messages_bnb': i.count_success_send_messages_bnb}
                )

        return data


async def clear_all_statistic():
    async with async_session() as session:        
        result = await session.scalars(select(User))
        for i in result:
            i.count_success_send_book = 0
            i.count_success_send_bnb = 0
            i.count_success_send_messages_book = 0
            i.count_success_send_messages_bnb = 0

        await session.commit()
        return True
    

async def add_count_success_send_book(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).filter_by(tg_id=tg_id))
        result.count_success_send_book += 1
        
        await session.commit()
        return True

async def add_count_success_send_bnb(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).filter_by(tg_id=tg_id))
        result.count_success_send_bnb += 1
        
        await session.commit()
        return True
    
async def add_count_success_send_messages_book(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).filter_by(tg_id=tg_id))
        result.count_success_send_messages_book += 1
        
        await session.commit()
        return True
    
async def add_count_success_send_messages_bnb(tg_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User).filter_by(tg_id=tg_id))
        result.count_success_send_messages_bnb += 1
        
        await session.commit()
        return True
