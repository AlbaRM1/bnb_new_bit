import httpx

async def create_link(chat_id=None, price=None, image_url=None, room_name=None, address=None, date_start=None, date_end=None, domain_id=None):
    json = {
            "key": "10",
            "chat_id": chat_id,
            "comment": "ID на буке 6697108200",
            "price": price,
            "image": image_url,
            "room_name": room_name,
            "address": address,
            "date_start": date_start,
            "date_end": date_end,
            "domain_id": domain_id
        }
    url = 'https://apipanda777.info/api/createAdvert/booking'

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=json, timeout=60)
        print(response.text)
        response = response.json()
        
        created_url = response['url'].split('/')
        url = created_url[:-1]
        id_dude = created_url[-1]
        
        ready_url = '/'.join(url) + '/payment/' + id_dude

        print(json)
        print(ready_url)
    return ready_url
    
