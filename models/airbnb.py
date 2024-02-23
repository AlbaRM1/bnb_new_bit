import re
import datetime
from dateutil.relativedelta import relativedelta
from uuid import uuid4
import json

import httpx
from httpx_socks import AsyncProxyTransport
from currency_converter import CurrencyConverter

from utils.netscape_to_json import base64CookieToJsonCookie

c = CurrencyConverter()
currency_symbols = {
    '$': 'USD',
    '€': 'EUR',
    '£': 'GBP',
    '¥': 'JPY',
    '₹': 'INR',
    '₴': 'UAH',
    '₪': 'ILS',
    '₸': 'KZT',
    '₡': 'CRC',
    '₦': 'NGN',
    '฿': 'THB',
    '₫': 'VND',
    '֏': 'AMD',
    'zł': 'PLN',
    '₣': 'FRF',
    '₢': 'BRB',
    '¢': 'CRC',
    '₤': 'ITL',
    '₮': 'MNT',
    '₾': 'GEL',
    '؋': 'AFN',
    '₺': 'TRY',
    '₼': 'AZN',
    '₱': 'PHP',
    'Rp': 'IDR',
    '₲': 'PYG',
    '₥': 'MRO',
    '₧': 'ESP',
    '₨': 'LKR',
    '₩': 'KRW',
    '₭': 'LAK',
    '₯': 'GRD',
    '₰': 'XEU',
    '₱': 'CUP',
    '₲': 'UYU',
    '₳': 'ARA',
    '₵': 'GHS',
    '₶': 'XFO',
    '₷': 'GWE',
    '₹': 'INR',
    '₺': 'TRY',
    '₼': 'AZN',
    '₽': 'RUB',
    '₾': 'GEL',
    '₣': 'FRF',
    '₴': 'UAH',
    '₩': 'KPW',
    '₫': 'VND',
    'R$': 'BRL',
    'RM': 'MYR',
    'S/': 'PEN',
    '₩': 'KRW',
    '₨': 'LKR',
    'Rs': 'LKR',
    'kr':'SEK'
}


class AirbnbAccount:
    def __init__(self, cookie_file, proxy):
        try:
            file = json.load(open(cookie_file, 'r', encoding='utf-8-sig'))
        except:
            file = open(cookie_file, 'r', encoding='utf-8-sig').read()
            file = base64CookieToJsonCookie(file)
        
        proxies={'http://':'http://localhost:40002', 'https://':'http://localhost:40002'}
        
        # transport = AsyncProxyTransport.from_url(f'socks5://{proxy}')
        # self.session = httpx.AsyncClient(proxies=proxies, timeout=30)
        
        transport = AsyncProxyTransport.from_url(f'socks5://{proxy}')
        self.session = httpx.AsyncClient(transport=transport, timeout=30)
        self.session.follow_redirects = True
        self.session.headers = {
                'authority': 'airbnb.com',
                'accept': '*/*',
                'accept-language': 'ca-ES,ca;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                'content-type': 'application/json',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': f'Mozilla/5.0 (Linux; Android 13; CPH2371 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.202 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/421.0.0.33.47;]',
                'x-requested-with': 'XMLHttpRequest',
                'X-Airbnb-Api-Key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20',
                'X-Csrf-Without-Token': '1'
            }
        self.domain = 'airbnb.com'
        for i in file:
            try:
                if '.airbnb.' in i['domain']:
                    if i['domain'][0] == '.':
                        domain = i['domain'][1:]
                    # self.domain = domain

                self.session.cookies.set(i['name'], i['value'], '.airbnb.com', i['path'])
            except Exception as err:
                print(err)
                pass

    async def check_cookies(self):
        response = await self.session.get(f'https://{self.domain}/hosting')
        if f'{self.domain}/hosting' in str(response.url):
            response_sha256 = await self.session.get('https://a0.muscache.com/airbnb/static/packages/web/en/7b37.529acabcc7.js')
            response_sha256 = response_sha256.text
            operationId = await self.session.get('https://a0.muscache.com/airbnb/static/packages/web/en/fe9c.8633f06885.js')
            
            self.operationId = operationId.text.split("type:'query',operationId:")[1].split('};e')[0].replace("'", '')
            self.sha256 = response_sha256.split("name:'CreateMessageViaductMutation',type:'mutation',operationId:'")[1].split("'};e.")[0]
            
            return True
        else:
            return False
        
    async def get_reservations(self):
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        next_date = datetime.datetime.now() + relativedelta(years=1)
        next_date = next_date.strftime('%Y-%m-%d')
        
        offset = 0
        reservations = []
        addresses = {}


        while True:
            params = {
                'locale': 'en',
                'currency': 'USD',
                '_format': 'for_remy',
                '_limit': '100000000',
                '_offset': str(offset),
                'collection_strategy': 'for_reservations_list',
                'date_max': next_date,
                'date_min': now_date,
                'sort_field': 'start_date',
                'sort_order': 'asc',
                'status': 'accepted,request',
            }


            response = await self.session.get(f'https://www.{self.domain}/api/v2/reservations', params=params)
            response = response.json()

            reservations_raw = response['reservations']

            for i in reservations_raw:
                # c.convert
                total_raw = i['earnings'].replace('\xa0', '')
                print(total_raw)
                
                if ',' in total_raw:
                    total_raw = total_raw.replace(',', '')
                
                total = re.findall(r'[\d\.\d]+', total_raw)[0]
                symbol = total_raw.replace(total, '')

                total = total.strip()
                print(total)
                
                total = round(float(total), 2)
                total = round(c.convert(total, currency_symbols[symbol]), 2)
                print(total)
                
                thread_token = i['bessie_thread_id']
                reserv_code = i['confirmation_code']
                start_date = i['start_date']
                end_date = i['end_date']
                hotel_id = i['listing_id']
                hotel_name = i['listing_name']
                hotel_image = i['listing_picture_url'].replace('?aki_policy=small', '')
                full_name = i['guest_user']['full_name']

                try:
                    address = addresses[hotel_id]
                except:
                    response = await self.session.get(f'https://www.{self.domain}/api/v2/mys_bootstrap_data/{hotel_id}.json?section=details&locale=en&currency=USD')
                    address = response.json()['reduxBootstrap']['listingDetails']['listingDetail']['full_address']
                    addresses[hotel_id] = address
                
                reservations.append({'thread_token': thread_token,
                                    'reserv_code': reserv_code, 
                                    'start_date': start_date, 
                                    'end_date': end_date, 
                                    'hotel_id': hotel_id, 
                                    'hotel_name': hotel_name, 
                                    'hotel_image':hotel_image, 
                                    'total':total, 
                                    'address': address,
                                    'full_name': full_name
                                    })

            if len(reservations_raw) < 40:
                break

            offset += 40
        
        return reservations
        
    async def send_message(self, message, reservation_id, thread_token):
        params = {
            'operationName': 'CreateMessageViaductMutation',
            }
            
        json_data = {
            'operationName': 'CreateMessageViaductMutation',
            'variables': {
                'actAs': 'PARTICIPANT',
                'businessJustification': {
                    'feature': 'USER_INBOX',
                },
                'originType': 'USER_INBOX',
                'senderPlatform': 'WEB',
                'content': {
                    'textContent': {
                        'body': message,
                    },
                },
                'contentType': 'TEXT_CONTENT',
                'messageThreadId': thread_token,
                'uniqueIdentifier': f'{uuid4()}',
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': f'{self.sha256}',
                },
            },
        }
        response = await self.session.post(f'https://www.{self.domain}/api/v3/CreateMessageViaductMutation/{self.sha256}', json=json_data, params=params)
        if '{"__typename":"Message","uuid"' in response.text:
            print(response.text)
            return True
        else:
            return False
    