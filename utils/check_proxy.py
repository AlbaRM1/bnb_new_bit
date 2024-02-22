import httpx
from httpx_socks import AsyncProxyTransport

async def check(proxy):
    transport = AsyncProxyTransport.from_url(f'socks5://{proxy}')
    session = httpx.AsyncClient(transport=transport, timeout=30)
    
    try:
        response = await session.get('https://icanhazip.com')
        return response.text.strip()
    except Exception as err:
        print(err)
        return False