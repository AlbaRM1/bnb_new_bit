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

def chunkify(lst,n):
    return [lst[i::n] for i in range(n)]

class AgodaAccount:
    def __init__(self, cookie_file, proxy):
        self.ua = UserAgent(os='windows')
        try:
            file = json.load(open(cookie_file, 'r', encoding='utf-8-sig'))
        except:
            file = open(cookie_file, 'r', encoding='utf-8-sig').read()
            file = base64CookieToJsonCookie(file)
        userag = 'Booking.Pulse/25.5 Android/9; Type: mobile; AppStore: google; Brand: ; Model:'
        
        print(proxy)
        transport = AsyncProxyTransport.from_url(f'socks5://{proxy}', retries=3)
            
        self.session = httpx.AsyncClient(transport=transport, timeout=60)
        # self.session = httpx.AsyncClient(proxies=proxies, timeout=30)
        self.session.follow_redirects = True
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://ycs.agoda.com/mldc/en-us/app/reporting/booking/',
            'content-type': 'application/x-www-form-urlencoded',
            'Origin': 'https://ycs.agoda.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            }
        
        for i in file:
            try:
                self.session.cookies.set(i['name'], i['value'], i['domain'], i['path'])
            except Exception as err:
                print(err)
                pass
    
    
    async def check_cookies(self):
        self.hotel_id = []
        try:
            response = await self.session.get('https://ycs.agoda.com')
            hotel_id = str(response.url).split('/')[-1]
            
            if hotel_id == 'propertysearch':
                self.session.headers['Content-type'] = 'application/json; charset=utf-8'
                
                data = {
                    'countryId': '',
                    'criteria':"",
                    'hotelTypeId':1
                }
                response = await self.session.post('https://ycs.agoda.com/mldc/en-us/api/iam/PropertySearch/Search', json=data)
                response = response.json()['hotelList']

                for i in response:
                    if i['hotelStatus'] == 'active':
                        self.hotel_id.append(i['hotelId'])
                
            else:
                self.hotel_id = [int(hotel_id)]
            
            return True
        except Exception as err:
            print(err)
            return False
        

    async def get_reservations(self):
        ready_data = []
        
        for hotelid in self.hotel_id:
            self.session.headers['Content-type'] = 'application/x-www-form-urlencoded'
            now_date = datetime.datetime.combine(datetime.date.today(), datetime.time(5)).timestamp()
            next_date = datetime.datetime.combine(datetime.date.today(), datetime.time(5)) + relativedelta(years=1)
            next_date = next_date.timestamp()

            now_date = str(now_date).split('.')[0] + '000'
            next_date = str(next_date).split('.')[0] + '000'

            data = {
                'BookingId': '',
                'CustomerName': '',
                'PaymentModel': '0',
                'UseCheckinDate': 'true',
                'UseRequestDate': 'false',
                'UseBookingDate': 'false',
                'CheckInDateFromJson': f'/Date({now_date})/',
                'CheckInDateToJson': f'/Date({next_date})/',
                'ChannelId': '0',
                'RateCategoeyId': '0',
                'RoomTypeId': '0',
                'BookingStayDateFilter': '0',
            }

            response = await self.session.post(f'https://ycs.agoda.com/en-us/{hotelid}/kipp/api/hotelBookingApi/Get/', data=data)
            response = response.json()
            reservations = response.get('Bookings', None)

            if reservations:
                bookingIds_list = []
                data_complete = {}

                for i in reservations:
                    if i['AckRequestType'] == 1 or i['AckRequestType'] == 3:
                        bookingIds_list.append({"bookingId": str(i['BookingId'])})
                
                url = f'https://ycs.agoda.com/en-us/{hotelid}/kipp/api/hotelBookingApi/GetDetails'
                bookingIds_str = str(bookingIds_list).replace('[', '').replace(']', '')

                get_details_raw_new = []
                print(bookingIds_list)
                
                try:
                    if len(bookingIds_list) > 100:
                        bookingIds = chunkify(bookingIds_list, round(len(bookingIds_list) / 100))    
                        
                        for i in bookingIds:
                            i_str = str(i).replace('[', '').replace(']', '')
                        
                            response = await self.session.post(url, data={'BookingDetailList': f'[{i_str}]'})
                            get_details_raw = response.json()
                            
                            get_details_raw = get_details_raw.get('Data', [])
                            get_details_raw_new += get_details_raw
                    else:
                        response = await self.session.post(url, data={'BookingDetailList': f'[{bookingIds_str}]'})
                        get_details_raw = response.json()
                        print(get_details_raw)
                        
                        get_details_raw = get_details_raw.get('Data', [])
                        get_details_raw_new += get_details_raw
                    
                    rate = False
                    for data_raw in get_details_raw_new:
                        try:
                            bookingId = data_raw['ApiData']['BookingId']
                            name = data_raw['FirstName'] + ' ' + data_raw['LastName']
                            checkin = data_raw['ApiData']['CheckInDateStr']
                            checkout = data_raw['ApiData']['CheckOutDateStr']
                            currency = data_raw['ApiData']['RateDetailList']['Currency']
                            conversation_id = data_raw['ConversationId']
                            
                            total = data_raw['ApiData']['RateDetailList']['TotalReferenceSellInclusive']
                            
                            if total == None:
                                total = data_raw['ApiData']['RateDetailList']['TotalSellInclusive']
                            
                            if total == None:
                                total = data_raw['ApiData']['RateDetailList']['TotalNetInclusive']
                                
                            
                            total = await convert_to_eur(str(total), currency, rate)
                            total, rate = total
                            
                            data_complete[bookingId] = {
                                'name': name,
                                'checkin': checkin,
                                'checkout': checkout,
                                'conversation_id': conversation_id,
                                'price': total
                            }
                        except Exception as err:
                            print(traceback.format_exc())
                            pass
                    
                    self.session.headers['Content-type'] = 'application/json; charset=utf-8'
                    
                    if len(bookingIds_list) > 100:
                        for i in bookingIds:
                            data = {
                                'externalId': int(hotelid),
                                'bookingAndPropertyDetails': i,
                                'isMobApp': False,
                                'languageId': 1,
                                'origin': 'YcsHermesIris',
                                
                            }

                            response = await self.session.post(
                                f'https://ycs.agoda.com/mldc/v1/chat/getBookingAndPropertyDetails',
                                json=data,
                            )
                            response = response.json()
                            
                            for i in response['bookingAndPropertyDetails']:
                                try:
                                    bookingId = i['bookingId']
                                    memberId = i['memberId']
                                    hotel_name = i['propertyName']
                                    hotel_image = i['propertyImageUrl'].replace('//', 'https://')
                                    hotel_address = i['propertyCity']
                                    
                                    ready_data.append({
                                            'name': data_complete[bookingId]['name'],
                                            'checkin': data_complete[bookingId]['checkin'],
                                            'checkout': data_complete[bookingId]['checkout'],
                                            'conversation_id': data_complete[bookingId]['conversation_id'],
                                            'price': data_complete[bookingId]['price'],
                                            
                                            'bookingId': bookingId,
                                            'memberId': memberId,
                                            'hotel_name': hotel_name,
                                            'hotel_image': hotel_image,
                                            'hotel_address': hotel_address,
                                            'hotel_id': hotelid
                                        })
                                except Exception as err:
                                    print(traceback.format_exc())
                                    pass
                    else:
                        data = {
                                'externalId': int(hotelid),
                                'bookingAndPropertyDetails': bookingIds_list,
                                'isMobApp': False,
                                'languageId': 1,
                                'origin': 'YcsHermesIris',
                                
                        }

                        response = await self.session.post(
                            f'https://ycs.agoda.com/mldc/v1/chat/getBookingAndPropertyDetails',
                            json=data,
                        )
                        response = response.json()
                        print(response)
                    
                        for i in response['bookingAndPropertyDetails']:
                            try:
                                bookingId = i['bookingId']
                                memberId = i['memberId']
                                hotel_name = i['propertyName']
                                hotel_image = i['propertyImageUrl'].replace('//', 'https://')
                                hotel_address = i['propertyCity']
                                
                                ready_data.append({
                                        'name': data_complete[bookingId]['name'],
                                        'checkin': data_complete[bookingId]['checkin'],
                                        'checkout': data_complete[bookingId]['checkout'],
                                        'conversation_id': data_complete[bookingId]['conversation_id'],
                                        'price': data_complete[bookingId]['price'],
                                        
                                        'bookingId': bookingId,
                                        'memberId': memberId,
                                        'hotel_name': hotel_name,
                                        'hotel_image': hotel_image,
                                        'hotel_address': hotel_address,
                                        'hotel_id': hotelid
                                    })
                            except:
                                pass
                except Exception as err:
                    print(response.text)
                    print(err)
                    pass
                
        return ready_data
    
    async def send_message(self, message, conversationId, memberId, bookingId, checkIn, checkOut, guestName, hotelName, hotel_id):
        self.session.headers['Content-type'] = 'application/json; charset=utf-8'
        print(message, conversationId, memberId, bookingId)
        
        checkIn = checkIn.split('-')
        checkIn[2] = checkIn[2][2:]
        checkIn[1] = f'{checkIn[1]},'
        checkIn = ' '.join(checkIn)
        
        checkOut = checkOut.split('-')
        checkOut[2] = checkOut[2][2:]
        checkOut[1] = f'{checkOut[1]},'
        checkOut = ' '.join(checkOut)
        
        json_data = {
            'conversationId': str(0),
            'memberId': int(memberId),
            'message': message,
            'bookingId': int(bookingId),
            'target': 'agoda:hermes',
            'origin': 'YcsHermesIris',
            'checkIn': checkIn,
            'checkOut': checkOut,
            'createConversationIfNotExist': True,
            'customerName': guestName,
            'propertyId': str(hotel_id),
            'propertyName': hotelName,
            "isVisibleTo":[ "guest", "host" ]
        }

        try:
            response = await self.session.post('https://ycs.agoda.com/mldc/v1/chat/sendMessage', json=json_data, timeout=15)
            print(response.text)
            
            if response.status_code == 200:
                return True
            else:
                return False
            
        except Exception as err:
            print(err)
            return False
        