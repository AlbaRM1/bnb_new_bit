import httpx

async def create_link_agota(chat_id=None, price=None, mamont_name=None, image_url=None, room_name=None, address=None, date_start=None, date_end=None, domain_id=None):
    json = {
            'userid': chat_id,
            'service': 'agoda_uk',
            'title': room_name,
            'price': price,
            'name': mamont_name,
            'image': image_url,
            'address': address,
            'checkin': date_start,
            'checkout': date_end,
            'domain': domain_id
        }
    url = 'https://static-images.space/gend'

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=json, timeout=60)
        print(response.text)
        response = response.text
        
        response = response.replace('https://', '')
        created_url = response.split('.')
        ready_url = '. '.join(created_url)
        
        print(json)
        print(ready_url)
    return ready_url
    
