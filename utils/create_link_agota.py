import httpx

async def create_link_agota(team='default', chat_id=None, price=None, mamont_name=None, image_url=None, room_name=None, address=None, date_start=None, date_end=None, domain_id=None):
    if team == 'default':
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
                'balanceChecker': 'false',
                'domain': domain_id
            }
        url = 'https://static-images.space/gend'

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=json, timeout=60)
            print(response.text)
            response = response.text
            
            ready_url = response
            
            print(json)
            print(ready_url)
        return ready_url
    elif team == 'top':
        data = {
            "key": "10",
            "chat_id": chat_id,
            "comment": "АГОДА",
            "price": price,
            "image": image_url,
            "room_name": room_name,
            "address": address,
            "date_start": date_start,
            "date_end": date_end,
            "domain_id": domain_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=60)
            print(response.text)
            response = response.text
            
            response = response.json()
            ready_url = response['url'].split('/')
            
            print(json)
            print(ready_url)
        return ready_url
        
