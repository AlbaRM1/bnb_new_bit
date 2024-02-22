import httpx

def create_link(chat_id=None, price=None, image_url=None, room_name=None, address=None, date_start=None, date_end=None, domain_id=None):
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

    response = httpx.post(url, json=json, timeout=60).json()
    print(json)
    print(response)
    return response['url']
    