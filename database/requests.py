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


async def add_text(tg_id: int, text: str):
    async with async_session() as session:
        result = await session.scalar(select(User).options(selectinload(User.texts)).filter_by(tg_id=tg_id))
        result.texts.append(Text(text=text))
        
        session.add(result)
        await session.commit()
        return True
    

async def del_text(text_id: int):
    async with async_session() as session:
        result = await session.scalar(select(Text).filter_by(id=text_id))
        
        await session.delete(result)
        await session.commit()
        return True