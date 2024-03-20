import traceback
import random
from asyncio import sleep
import httpx
import json
from uuid import uuid4
from bs4 import BeautifulSoup as bs
from datetime import datetime
from httpx_socks import AsyncProxyTransport
from fake_useragent import UserAgent
from dateutil.relativedelta import relativedelta

from utils.netscape_to_json import base64CookieToJsonCookie
from utils.value_to_eur import convert_to_eur



class BookingAccount:
    def __init__(self, cookie_file, proxy, type_proxy='socks'):
        self.ua = UserAgent(os='windows')
        try:
            file = json.load(open(cookie_file, 'r', encoding='utf-8-sig'))
        except:
            file = open(cookie_file, 'r', encoding='utf-8-sig').read()
            file = base64CookieToJsonCookie(file)
        userag = self.ua.firefox.strip()
        
        print(proxy)
        print(userag)
        
        if type_proxy == 'socks':
            transport = AsyncProxyTransport.from_url(f'socks5://{proxy}')
        elif type_proxy == 'pia':
            transport = AsyncProxyTransport.from_url(f'http://{proxy}')
            
        self.session = httpx.AsyncClient(transport=transport, timeout=30)
        # self.session = httpx.AsyncClient(proxies=proxies, timeout=30)
        self.session.follow_redirects = True
        self.session.headers = {
                'Origin':'https://admin.booking.com',
                'Accept-Encoding':'gzip, deflate, br',
                'accept': '*/*',
                'accept-language': 'es-PE,es-MX;q=0.9,es;q=0.8',
                'content-type': 'application/json',
                'sec-ch-ua-mobile': '?0',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'User-Agent': userag,
                'Upgrade-Insecure-Requests': "1",
                'x-requested-with': 'XMLHttpRequest',
                'x-booking-context-action-name': 'hhemm_inbox',
                'x-booking-topic': 'extranet-messaging-inbox-ui',
            }
        for i in file:
            try:
                self.session.cookies.set(i['name'], i['value'], i['domain'], i['path'])
            except Exception as err:
                print(err)
                pass
                

    async def get_reservations(self):
        reservations = []
        offset = 0
        
        hotel_data = self.hostels[0]
        rate = False
        while True:
            try:
                params = {
                    'ses': self.sess_id,
                    'lang': 'xu',
                    'hotel_id': hotel_data['id']
                }

                response = await self.session.post(
                    'https://admin.booking.com/fresa/extranet/property/snooze_listing/get_info',
                    params=params,
                )
                data = response.json()['data']['hotel_data']
                
                image_url = data['mainPhoto'].replace('square150', 'square1024')
                address = data['fullAddress']

                now_date = datetime.now().strftime('%Y-%m-%d')
                next_date = datetime.now() + relativedelta(years=1)
                next_date = next_date.strftime('%Y-%m-%d')
                
                json_data = {
                    'operationName': 'searchReservations',
                    'variables': {
                        'paymentStatusFeatureActive': True,
                        'input': {
                            'accountId': int(self.account_id),
                            'typeOfDate': 'ARRIVAL',
                            'dateFrom': str(now_date),
                            'dateTo': str(next_date),
                            'onlyPendingRequests': False,
                            'statusCriteria': {
                                'showCancelled': False,
                                'showOk': True,
                                'showNoShow': False,
                                'showPaidOnline': False,
                            },
                            'pagination': {
                                'rowsPerPage': 200,
                                'offset': offset,
                            },
                        },
                    },
                    'extensions': {},
                    'query': 'query searchReservations($input: SearchReservationInput!, $paymentStatusFeatureActive: Boolean = false) {\n  partnerReservation {\n    searchReservations(input: $input) {\n      properties {\n        address\n        countryCode\n        cityName\n        extranetHomeUrl\n        status\n        name\n        id\n        __typename\n      }\n      reservations {\n        actualCommission\n        aggregatedRoomStatus\n        amountInvoicedOrRoomPriceSum\n        amountInvoicedOrRoomPriceSumRaw\n        bookerFirstName\n        bookerLastName\n        commissionAmount\n        commissionAmountRaw\n        createdAt\n        currencyCode\n        propertyId\n        id\n        isGeniusUser\n        checkout\n        checkin\n        occupancy {\n          guests\n          adults\n          children\n          childrenAges\n          __typename\n        }\n        pendingGuestRequestCount\n        paymentStatus @include(if: $paymentStatusFeatureActive)\n        __typename\n      }\n      reservationsHavePaymentCharge\n      totalRecords\n      __typename\n    }\n    __typename\n  }\n}\n',
                }

                response = await self.session.post(
                    'https://admin.booking.com/dml/graphql.json',
                    params=params,
                    json=json_data
                )
                
                response = response.json()
                print(response)
                
                reservations_raw = response['data']['partnerReservation']['searchReservations']['reservations']
                
                for i in reservations_raw:
                    first_name = i['bookerFirstName']
                    last_name = i['bookerLastName']
                    
                    price = i['amountInvoicedOrRoomPriceSumRaw']
                    price_currency = i['currencyCode']
                    image = image_url
                    room_name = hotel_data['hotel_name']
                    address = address
                    date_start = i['checkin']
                    date_end = i['checkout']
                    name = f'{first_name} {last_name}'
                    id_guest = str(i['id']).replace(')', '').replace('(', '').replace(',', '').replace("'", ''),
                    hotel_name = hotel_data['hotel_name']
                    hotel_id = hotel_data['id']
                    
                    price = await convert_to_eur(price, price_currency, rate)
                    price, rate = price
                    print(id_guest)
                        
                    reservations.append({
                        'price': price,
                        'image': image,
                        'room_name': room_name,
                        'address': address,
                        'date_start': date_start,
                        'date_end': date_end,
                        'name': name,
                        'id_guest': id_guest,
                        'hotel_name': hotel_name,
                        'hotel_id': hotel_id
                    })
                    
                if len(reservations_raw) < 200:
                    break
                
                offset += 1
                    
            except Exception as err:
                print(traceback.format_exc())
                print(response)
                return False
            
        return reservations


    async def get_hostels(self):
        self.hostels = []
        
        json_data = {
            'operationName': 'groupHomeListProperties',
            'variables': {
                'input': {
                    'accountId': self.account_id,
                    'searchTerm': '',
                    'showClosed': True,
                    'sortDirection': 'DESC',
                    'sortType': 'PROPERTY_ID',
                    'states': [],
                    'ufis': [],
                    'accommodationTypeIds': [],
                    'pagination': {
                        'offset': 0,
                        'rowsPerPage': 30,
                    },
                    'availabilityStatus': 'OPEN_BOOKABLE',
                },
            },
            'extensions': {},
            'query': 'query groupHomeListProperties($input: GroupHomeListPropertiesInputV2!) {\n  partnerProperty {\n    groupHomeListPropertiesV2(input: $input) {\n      properties {\n        address\n        arrivalsUrl\n        departuresUrl\n        reservationsUrl\n        inboxUrl\n        cityName\n        countryCode\n        id\n        name\n        extranetHomeUrl\n        status\n        __typename\n      }\n      recordsFiltered\n      __typename\n    }\n    __typename\n  }\n}\n',
        }
        params = {
            'lang': 'hr',
            'ses': self.sess_id,
        }   
        response = await self.session.post('https://admin.booking.com/dml/graphql.json', params=params, json=json_data)
        response = response.json()['data']['partnerProperty']['groupHomeListPropertiesV2']['properties']
        
        for hotel in response:
            hotel_data = {'id': hotel["id"], 'hotel_name': hotel["name"]}
            self.hostels.append(hotel_data)
            
        return self.hostels
    
    
    async def check_cookies(self):
        response = await self.session.get('https://icanhazip.com')
        print(response.text)
        try:
            response = await self.session.get('https://admin.booking.com/')
            self.sess_id = str(response.url).split('ses=')[1].split('&')[0]
            soup = bs(response.text, 'html.parser')
            
            if "hotel_id" in str(response.url):
                self.hotel_id = str(response.url).split('hotel_id=')[1].split('&')[0]
                hotel_name = soup.select('#main-content > div > div > div.homepage-main-column.bui-grid__column-full.bui-grid__column-9\@huge > div > div > div.bui-page-header.bui-spacer.peg-page-header > h1')[0]
                hotel_name.span.decompose()
                hotel_name = hotel_name.get_text().strip()
                hotel_name = hotel_name.replace('\\', '').replace('"', '')
                
                self.account_id = response.text.split('"account_id":')[1].split(',"')[0].replace('}', '')
                
                self.hostels = []
                self.hostels.append({'id': self.hotel_id, 'hotel_name': hotel_name})
                
                return {'status': True, 'need': None, 'hotel_name': hotel_name}
            else:
                script = soup.find('script', attrs={'type': 'application/json'})
                script_json = json.loads(script.get_text())

                self.account_id = script_json['partnerIdentity']['partnerAccountId']
                hostels = await self.get_hostels()

                return {'status': True, 'hotel_name': hostels[0]['hotel_name']}
            
        except Exception as err:
            print(traceback.format_exc())
            return {'status': False, 'need': None}
        

    async def send_messages(self, message, product_id, hotel_id):
        await sleep(random.uniform(1,5))
        
        while True:
            try:
                # await sleep(random.uniform(1, 5))
                params = {
                    'ses': self.sess_id,
                    'et_init': '1',
                    'lang': 'en',
                }
                json_data = {
                    'operationName': 'postFreeTextMessage',
                    'variables': {
                        'input': {
                            'content': f'{message}',
                            'actor': {
                                'actorId': int(hotel_id),
                                'actorType': 'HOTEL',
                            },
                            'conversationReference': {
                                'conversationType': 'GUEST_PARTNER_CHAT',
                                'productType': 'ACCOMMODATION',
                                'productId': str(product_id).replace(')', '').replace('(', '').replace(',', '').replace("'", ''),
                            },
                            'idempotency': str(uuid4()),
                        },
                    },
                    'query': 'mutation postFreeTextMessage($input: ChatPostFreeTextMessageInput!) {\n    chatMessage {\n      postFreeTextMessage(input: $input) {\n        message {\n          content\n          inReplyToMessageId\n          messageId\n          conversationReference {\n            conversationType\n            productType\n            productId\n          }\n        }\n      }\n    }\n  }\n',
                }
                response = await self.session.post(
                    'https://admin.booking.com/dml/graphql.json',
                    params=params,
                    json=json_data,
                )
                print(response.headers)
                print(response.text)
                if '"postFreeTextMessage"' in response.text:
                    return {'status': True, 'product_id': product_id}
                elif 'We got a 403' in response.text:
                    return {'status': False, 'reason': 'edit_proxy', 'product_id': product_id}
                elif 'We got a 401' in response.text:
                    return {'status': False, 'reason': 'not_in_account', 'product_id': product_id}
                else:
                    return {'status': False, 'reason': 'not_known', 'product_id': product_id}
            except Exception as err:
                print(err)
                print('retry now!')
                pass