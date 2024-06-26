from bs4 import BeautifulSoup as bs
import traceback
import re
import datetime
from dateutil.relativedelta import relativedelta
from uuid import uuid4
import json

from fake_useragent import UserAgent

import httpx
from httpx_socks import AsyncProxyTransport
from utils.value_to_eur import convert_to_eur

from utils.netscape_to_json import base64CookieToJsonCookie

class AirbnbAccount:

    def __init__(self, cookie_file, proxy):
        self.ua = UserAgent()
        try:
            file = json.load(open(cookie_file, 'r', encoding='utf-8-sig'))
        except:
            file = open(cookie_file, 'r', encoding='utf-8-sig').read()
            file = base64CookieToJsonCookie(file)
        
        proxy = proxy.replace('socks5://', '')
        # proxies={'http://': f'socks5://{proxy}', 'https://': f'socks5://{proxy}'}
        
        # transport = AsyncProxyTransport.from_url(f'socks5://{proxy}')
        # self.session = httpx.AsyncClient(proxies=proxies, timeout=30)
        
        transport = AsyncProxyTransport.from_url(f'socks5://{proxy}')
        ua_rand = self.ua.random
        print(ua_rand)

        self.session = httpx.AsyncClient(transport=transport, timeout=30)
        self.session.follow_redirects = True
        self.session.headers = {
                'authority': 'airbnb.com',
                'Origin': 'https://www.airbnb.com',
                'Referer': 'https://www.airbnb.com/',
                'accept': '*/*',
                'accept-language': 'ca-ES,ca;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                'content-type': 'application/json',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                # 'user-agent': ua_rand,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
                'X-Airbnb-Api-Key': 'd306zoyjsyarp7ifhu67rjxn52tv0t20',
                'X-Csrf-Without-Token': '1',
            }
        self.domain = 'airbnb.com'
        for i in file:
            try:
                if '.airbnb.' in i['domain']:
                    if i['domain'][0] == '.':
                        domain = i['domain'][1:]
                    self.domain = domain

                self.session.cookies.set(i['name'], i['value'], i['domain'], i['path'])
            except Exception as err:
                print(traceback.format_exc())
                pass
        
        self.domain = self.domain.replace('www.', '')

    async def check_cookies(self):
        print(self.domain)
        response = await self.session.get(f'https://www.{self.domain}/hosting')
        if f'{self.domain}/hosting' in str(response.url) and response.status_code == 200:
            response_sha256 = await self.session.get('https://a0.muscache.com/airbnb/static/packages/web/en/7b37.529acabcc7.js')
            response_sha256 = response_sha256.text
            operationId = await self.session.get('https://a0.muscache.com/airbnb/static/packages/web/en/fe9c.8633f06885.js')
            
            self.operationId = operationId.text.split("type:'query',operationId:")[1].split('};e')[0].replace("'", '')
            self.sha256 = response_sha256.split("name:'CreateMessageViaductMutation',type:'mutation',operationId:'")[1].split("'};e.")[0]
            
            return True
        else:
            return False
    
    async def get_currency(self):
        #params = {
        #    'operationName': 'HostConsoleSectionsQuery',
        #    'variables': '{"currentUrl":"/hosting/reservations","sectionIds":["globalBanner","globalBannerModalHeader","globalBannerModalActions","notifications"],"mockIdentifier":null,"skipAnnouncements":true,"announcementRequest":{"surface":"TODAYTAB"}}',
        #    'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"17fc61469a9d6228f493d6870013baf09b7132554f2772018bef7445e6efce11"}}',
        #}
        #response = await self.session.get(f'https://www.{self.domain}/api/v3/HostConsoleSectionsQuery/17fc61469a9d6228f493d6870013baf09b7132554f2772018bef7445e6efce11', params=params)
        #response = response.json()

        #currency = response['data']['presentation']['staysHostConsole']['staysHostNavigationSections']['sections'][0]['section']['sections'][3]['section']['menuItemGroups'][1]['menuItems'][1]['title']
        #currency = re.findall(r'[\w]{3}', currency)[0]

        response = await self.session.get(f'https://{self.domain}/')

        soup = bs(response.text)
        curr = soup.find('script', attrs={'id': 'data-injector-instances'})
        curr = curr.getText()

        curr = json.loads(curr)
        curr = curr['root > core-guest-spa'][1][1]['userAttributes']['curr']

        return curr


    async def get_reservations(self):
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        next_date = datetime.datetime.now() + relativedelta(years=1)
        next_date = next_date.strftime('%Y-%m-%d')
        
        offset = 0
        reservations = []
        addresses = {}
        currency = await self.get_currency()
        print(currency)

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
            print(response.text)
            response = response.json()

            reservations_raw = response['reservations']

            for i in reservations_raw:
                try:
                    # if i['host_calendar_reservation_status'] == 'STATUS_FUTURE':
                    # c.convert
                        total_raw = i['earnings'].replace('\xa0', '')
                        print(total_raw)
                        
                        total = await convert_to_eur(total_raw, currency)
                        print(total)
                        
                        thread_token = i['bessie_thread_id']
                        reserv_code = i['confirmation_code']
                        start_date = i['start_date']
                        end_date = i['end_date']
                        hotel_id = i['listing_id']
                        hotel_name = i['listing_name']
                        hotel_image = i.get('listing_picture_url', '').replace('?aki_policy=small', '')
                        full_name = i['guest_user']['full_name']

                        try:
                            address = addresses[hotel_id]
                        except Exception as err:
                            response = await self.session.get(f'https://www.{self.domain}/api/v2/mys_bootstrap_data/{hotel_id}.json?section=details&locale=en&currency=USD')
                            print(response)
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
                except Exception as err:
                    print(err)
                    pass
            if len(reservations_raw) < 40:
                break

            offset += 40
        
        return reservations
        
    async def send_message(self, message, reservation_id, thread_token):
        self.session.cookies.delete('everest_cookie')
        # useragent = self.ua.unknown
        # print(useragent)

        # self.session.headers['user-agent'] = useragent

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
        # elif '"error_code":420' or "You don't have permission to access" in response.text:
        #     pass
        else:
            print(response.text)
            return False
    