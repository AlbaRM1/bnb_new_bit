import asyncio
import random
from aiogram import types
from bs4 import BeautifulSoup as bs
import traceback
import re
import datetime
from dateutil.relativedelta import relativedelta
from uuid import uuid4
import json

import httpx
from httpx_socks import AsyncProxyTransport
from utils.value_to_eur import convert_to_eur

from utils.netscape_to_json import base64CookieToJsonCookie


class ExpediaAccount:
    def __init__(self, cookie_file, proxy):
        try:
            file = json.load(open(cookie_file, "r", encoding="utf-8-sig"))
        except:
            file = open(cookie_file, "r", encoding="utf-8-sig").read()
            file = base64CookieToJsonCookie(file)

        # proxies={"http://":"http://localhost:40002", "https://":"http://localhost:40002"}
            
        print(proxy)
        transport = AsyncProxyTransport.from_url(f'socks5://{proxy}', retries=3)
            
        self.session = httpx.AsyncClient(transport=transport, timeout=60)
        self.session.follow_redirects = True
        self.session.headers = {
                    'accept': '*/*',
                    'accept-language': 'en-AU,en;q=0.9',
                    'cache-control': 'max-age=0',
                    'content-type': 'application/json',
                    # 'cookie': 'epc.messagecenter.pwa=true; _csrfToken=9347f8f78500633105b0658b3e2647ef; MC1=GUID=d0e725e3f06b4e1fa269c00cfa7310e2; DUAID=d0e725e3-f06b-4e1f-a269-c00cfa7310e2; linfo=v.4,|0|0|255|1|0||||||||1033|0|0||0|0|0|-1|-1; EPCSession=c771d5fddc81443ebab8af8914bb4265; cookie_prompt=enabled; ak_bmsc=7DD59802F5250AB9516DA56C6DC960C0~000000000000000000000000000000~YAAQOk5haKxE23+OAQAApWENoBcM22XxpFwYPTaDrwWU34RhGlMiglkL1kGqXnP5yEkLwBYY3zHuCFBBdX/MZYnjOeInceLU7OjNcWRlLmQkxMagT5yK4Smi2XXOgoh4DgCF1jH7yeZ4mKnQZ8cPhkdKbB51r/zivYejtS7hKcHPrVfG6obGcM8ZCRF2NJBdiayhvfqcWdeNItdqn1V0abBvvFESGHw9/Lbuqzz+kwZLGntGuUJ3jK6SHd7adt5xmZCoX23oafkGSwGjEDZS4MISZDgypBaG/NUCFBwf9ENdysSi2yonpnSUUcnTqbO4Y+JRYz7xbBZKLpmSUlu5f5emxi3YJ+oEpAZ8FMDR6bDxr5obdOD82ooE/mY38Bw54PF7X0hhFftW0bnX10+tbAZ+5jKDHqNil9A=; osano_consentmanager_uuid=5c5cd01e-c47f-4524-9bfa-f0ba9285563f; osano_consentmanager=CUrFN2lD4xFEVQTwHPXT52FHcBU27aWFL07mRk-omRI7RZTcng4Ba6maLNEZBCCctTNqPdJ2ZSpkkPUUQzZe3PlsM34MCFQOs7iCwhx4Z2WWCcu6HHf_zUYice2thofJovGe__zImx5pPc-wpnQy0JNN9TkBnX3J5kSpkani415HYmxlCln3b-NJ30K-ZMlzOzdETXx2m-sEEgyXUnH1wsvEt38ScH64B4V2kguIWvRljhH8GK_wxKC0dwmy_Fc2kHTs3z28TyeybT4h-CW-BVn2I6Er_i4nFsQmAA==; _ga=GA1.2.2088148447.1712082223; _gid=GA1.2.2019271730.1712082223; QuantumMetricSessionID=f85ad8697b38780b1ab6105c79d819c2; QuantumMetricUserID=ed9d1b540c776ac27818308451493eb1; user=v.8,0,EX0136370B58$7F$14001000p$EE$25$0A$1C$33$234$1C$33$234$1C$33$234$21O001000$1E31!90KG$1B$88$F6$E1W$88!i02000; minfo=v.5,EX01A4D21D2E$CAj$0E.$CBQ$9A$11$EDA$C2$7C$CD!2$31u$7B$40$FB$9Ah$95$31$2A$5Dy$24$2AiuYv$3B$8B$B9z$169$DA$8A$26!2$93N$A1m$F0$D6K$3B$0E$24$CFyC$E5e$3E$A7L$3B; accttype=v.2,3,1,EX0152CAF17F$CAj$0E.$D6Q$81$11$F1A$C1$7C$CB$39$31g$7F$40$FB$94h$95$3B$2AVy$24$2BiuYA$3B$8B; _abck=14ED5614966B8492BD4CB92CEB27AFB8~0~YAAQOk5haINF23+OAQAAL2cOoAvvjDbwv5KGJAhdE3OmK85D9YHz80WQEU5SawS6W2z+JoLMUd8hW+EJ/s1UxI61sXKNgaJoELHJXKVo7L3H5o+/zNUXaQMIpvNBKqUSFpR8iyoCoyBVyIy4ujfTCzCB4Gwx/bAaD8SCQVf3yIBjjWnW0JwNHIpOouXTdkdYkGpt0ftiNKWsjVhxpop7MVBuIqYlPqkYfVbhCPgRMkMej0fGVcj3u/B2btEi7W8CfC/lJAIutyTcA7VUkke5XQDLgBRWz3LRQT0LrJvCd09+v2LulSXyzBhekT3DhtBPOAEwqk86dWKFumnNWaxVUiszeuDwroCMKi/m2WdspdsAAdzvsp13DKIsu+8JqQfWwUPTFxsXv+PK0giSRClYLTFIM12MASvIqCxyh5dteZ77GBkreLc9~-1~-1~-1; mdid=dP1ThpKJxSVN88_RQikeIwiUh_6nNy1mImPBrdgcDpflq6UTT99DDjJvIS-jsTy2K3hEAvhcB79ZNSwmhIewog; EG_SESSIONTOKEN=OselewzXETyynnneEVrq57BxfmaZixpFYWoPMCfUntE:Bfh7iJfz5D-4z9EnZbs5DbLSZEcQCdQSII-cnfXKvCssGxGNIaZEO5GdqYHccwsvfZgr9xMwU8kR6_0l2vbxOg; EPC.ALP.13129008=Y; CRQSS=e|1; CRQS=t|101`s|2056`l|en_US`c|USD; currency=USD; iEAPID=1; tpid=v.1,101; VSUPID=|0|69415708|13129008; Nav_open=Y; QSI_HistorySession=https%3A%2F%2Fapps.expediapartnercentral.com%2Flodging%2Freservations%2FlegacyReservationDetails.html%3Fhtid%3D13129008%26reservationIds%3D206478960~1712082428307; JSESSIONID=BA2F659A215B2764BE855E4218C9E97B; bm_sz=7696466FD78DC755E1E0422E5B9366B8~YAAQOk5haARI23+OAQAANPMQoBekvJe76ckuQHxnoO0bYwxRDpkJ4Gd/SdECyjQAK/8IGQQSH6NUBhPc6KJQuEPL3Wnsu9FOxJ1g2b+Zaij1aK0xaAhyox7JvbCifsO/QtTHnU314HWjz4DOweixuMS25n0SyWA/29bXSRMMHFDNxxmhRQsnA9SuTHWgvlqlG28TTQzJQ+UJD8NJ+G5GEkTpdPX44R2+8BH+xPUhoJW2hRh5H0pH2sPNTaCvm2jI2gdHX3CcOaGMiZ85t70Tt00Tr+msQ2axkNh1gpObaQi4qxE5ZRPQizzWtaIcsIAR5X5PViDQP/FzAcUKXRRhRNvTkcz2VGt4FUX5+OMyjI9H305kFmrmt//0FcOYIYq8OYYmdiJLIbttfrQBU1w9vt0DZcMnW8w7tLGLmieL0S2/reLUilx4slZl+ElzfY5CpMvPnrqA+0AVHA3+7aw9Yr/0Cb5mzQkGgyzpc4RHAdKTsnEqg5z0ug==~4601667~4602180; epcsid=eyJraWQiOiJlc3MtZGlyMSIsImFsZyI6ImRpciIsImVuYyI6IkExMjhDQkMtSFMyNTYifQ..oR1pq-iW3YI0kL3qiTVJJw.zCrlKbX7OdkSf422jDykGYtNVwTjDk2zoHaMyo5SwiDD8HGBe-mwbhtLgnVEPvyY4-lXAWKQFJ1PjJ5OF7LTt37t6p514vSyAWQp_-gBGDRL31G7N4Nzcq9gmGA7FiMMzSSiZeH8F5eAzip6K72iVyqCAscdDMeJDPmzWTaY7wxoP3DtbllmzTFGJ1yaQCLqSoSKCV1XB2AJdInPpBMUcHVwy5W3gyVdwEdSjDNRmLI8Mx4ExLD2U2t641DRoV5JKG4H-c1oMOUFWD9W0YqooA.dsBadlrfCttgFZBXWBS_vw; _dd_s=rum=2&id=b01a9b38-719e-46f2-b5b4-2519fdab7694&created=1712082425425&expire=1712083325425; bm_sv=AC3CA27977457A9CB18C85E6AAE59063~YAAQOk5haNdI23+OAQAACzMSoBc8kONWcO+mKr5fFEIuOD8+tX7gnLoSTE8vJ9Q27TagTYex1sCNwCsO3ly7SYqww2wzyvKUMwucvyxfBciF0SadUFx2NmcTJK6Xnq5RqBBqH7Ae7y7RGsOqMBszdpj2hRQsuDxux53lKEaNTumL9+TMX6UfxWxWqh8kh/wcCKxUOL5nmUVeHesmfq4RNNygM4Ppfb2eW8YqLKBSAUCsZItuZR+3TtGOWa5WJuZnLY8MqMAyoDVWTd33o3QFvQ==~1; _gat=1',
                    'origin': 'https://apps.expediapartnercentral.com',
                    'referer': 'https://apps.expediapartnercentral.com/lodging/conversations/messageCenter.html?htid=13129008&cid=f3219737-5a98-4b57-b141-13eb48e567f8&cpcePartnerId=80f78fe0-c362-493d-92d9-877a2922f2ce',
                    'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'same-origin',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
                    }

        for i in file:
            try:
                self.session.cookies.set(i["name"], i["value"], i["domain"], i["path"])
            except Exception as err:
                print(err)
                pass

    

    async def check_cookies(self):
        try:
            response = await self.session.get("https://apps.expediapartnercentral.com/")
            self.htid = str(response.url).split('?htid=')[1]
            self.userId = str(response.text).split("userId: '")[1].split("'")[0]
            self.session.headers['htid'] = self.htid
            
            r = await self.session.get(f'https://apps.expediapartnercentral.com/lodging/conversations/messageCenter.html?htid={self.htid}')
            csrf_token = str(r.text).split('csrfToken:"')[1].split('"')[0]
            self.session.headers["csrf-token"] = csrf_token
            
            return True
        except:
            return False
    
    
    async def create_chat(self, data):
        params = {
            'htid': self.htid,
        }
        json_data = {
            'authorUserId': self.userId,
            'reservationId': data['reservationItemId'],
            'propertyId': int(self.htid),
        }
        try:
            response = await self.session.post(
                'https://apps.expediapartnercentral.com/lodging/bookings/conversation/spcs-create',
                params=params,
                json=json_data,
            )
            
            if response.status_code == 200:
                response = response.json()
                data['conversation_id'] = response['conversationId']
                data['cpce_id'] = response['cpcePartnerId']
            return data
        except:
            return False
    
    async def get_reservations(self, message: types.Message):
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        next_date = datetime.datetime.now() + relativedelta(years=1)
        next_date = next_date.strftime('%Y-%m-%d')
        
        ready_data = []
        not_create_chat = []
        
        hotels_info = {}
        rate = False
        
        self.session.headers['client-name'] = 'pc-reservations-web'

        json_data = {
            'query': 'query getReservationsBySearchCriteria {reservationSearchV2(input: {propertyId: '+self.htid+', booked: true, bookingItemId: null, canceled: true, confirmationNumber: null, confirmed: true, startDate: "'+now_date+'", endDate: "'+next_date+'", dateType: \"checkIn\", evc: false, expediaCollect: true, timezoneOffset: \"+10:00\", firstName: null, hotelCollect: true, isSpecialRequest: false, isVIPBooking: false, lastName: null, reconciled: false, readyToReconcile: false, returnBookingItemIDsOnly: false, searchParam: null, unconfirmed: true searchForCancelWaiversOnly: false }) { reservationItems{ reservationItemId reservationInfo {reservationTpid propertyId startDate endDate createDateTime brandDisplayName newReservationItemId country reservationAttributes {businessModel bookingStatus fraudCancelled fraudReleased stayStatus eligibleForECNoShowAndCancel strongCustomerAuthentication invoiced} specialRequestDetails accessibilityRequestDetails product {productTypeId unitName bedTypeName propertyVipStatus} customerArrivalTime {arrival}readyToReconcile epsBooking } customer {id guestName phoneNumber email emailAlias country} loyaltyInfo {loyaltyStatus vipAmenities} confirmationInfo {productConfirmationCode} conversationsInfo {conversationsSupported id unreadMessageCount conversationStatus cpcePartnerId}totalAmounts {totalAmountForPartners {value currencyCode}totalCommissionAmount {value currencyCode}totalReservationAmount {value currencyCode}propertyBookingTotal {value currencyCode}totalReservationAmountInPartnerCurrency {value currencyCode}}reservationActions {requestToCancel {reason actionSupported actionUnsupportedBehavior {hide disable}}changeStayDates {reason actionSupported}requestRelocation {reason actionSupported}actionAttributes {highFence}reconciliationActions {markAsNoShow {reason actionSupported actionUnsupportedBehavior {hide disable openVa}virtualAgentParameters {intentName taxonomyId}}undoMarkNoShow {reason actionSupported actionUnsupportedBehavior {hide disable}}changeCancellationFee {reason actionSupported actionUnsupportedBehavior {hide disable}}resetCancellationFee {reason actionSupported actionUnsupportedBehavior {hide disable}}markAsCancellation {reason actionSupported actionUnsupportedBehavior {hide disable}}undoMarkAsCancellation {reason actionSupported actionUnsupportedBehavior {hide disable}}changeReservationAmountsOrDates {reason actionSupported actionUnsupportedBehavior {hide disable}}resetReservationAmountsOrDates {reason actionSupported actionUnsupportedBehavior {hide disable}}}}reconciliationInfo {reconciliationDateTime reconciliationType}paymentInfo {evcCardDetailsExist expediaVirtualCardResourceId creditCardDetails { viewable viewCountLimit viewCountLeft viewCount hideCvvFromDisplay valid prevalidateCardOptIn cardValidationViewable inViewingWindow validationInfo {validationStatus validationType validationDate validationBy hasGuestProvidedNewCC newCreditCardReceivedDate is24HoursFromLastValidation } }}billingInfo {invoiceNumber }cancellationInfo {cancelDateTime cancellationPolicy {priceCurrencyCode costCurrencyCode policyType cancellationPenalties {penaltyCost penaltyPrice penaltyPerStayFee penaltyTime penaltyInterval penaltyStartHour penaltyEndHour }nonrefundableDatesList}}compensationDetails {reservationWaiverType reservationFeeAmounts {propertyWaivedFeeLineItem {costCurrency costAmount }}} searchWaiverRequest {serviceRequestId type typeDetails state orderNumber partnerId createdDate srConversationId lastUpdatedDate notes {text author {firstName lastName }}}} numOfCancelWaivers}}',
            'variables': {},
        }

        response = await self.session.post(
            'https://api.expediapartnercentral.com/supply/experience/gateway/graphql',
            json=json_data,
        )
        
        reservations_raw = response.json()['data']['reservationSearchV2']['reservationItems']
        print(f'COUNT_RESERVATIONS -> {len(reservations_raw)}')
        
        if len(reservations_raw) < 500:
            for reservation in reservations_raw:
                hotel_prop_id = reservation['reservationInfo']['propertyId']
                hotel_info = hotels_info.get(hotel_prop_id, None)
                
                if hotel_info:
                    address = hotel_info['address']
                    img = hotel_info['img'],
                    hotel_name = hotel_info['hotel_name']
                else:
                    hotel_info = await self.get_hotels_info(hotel_prop_id)
                    hotels_info[hotel_prop_id] = hotel_info
                    
                    address = hotel_info['address']
                    img = hotel_info['img']
                    hotel_name = hotel_info['hotel_name']
                
                full_name = reservation['customer']['guestName']
                start_date = reservation['reservationInfo']['startDate']
                end_date = reservation['reservationInfo']['endDate']
                
                price_data = reservation['totalAmounts']['totalReservationAmountInPartnerCurrency']
                currency = price_data['currencyCode']
                room_name = reservation['reservationInfo']['product']['unitName']
                
                total = await convert_to_eur(str(price_data['value']), currency, rate)
                total, rate = total
                
                if reservation['conversationsInfo']['conversationsSupported']:
                    if reservation['reservationInfo']['reservationAttributes']['stayStatus'] != 'cancelled':
                        conversation_id = reservation['conversationsInfo']['id']
                        cpce_id = reservation['conversationsInfo']['cpcePartnerId']
                        
                        if not conversation_id:
                            not_create_chat.append({
                                    'address': address,
                                    'image_url': img,
                                    'full_name': full_name,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'room_name': room_name,
                                    'price': total,
                                    'conversation_id': conversation_id,
                                    'cpce_id': cpce_id,
                                    'hotel_name': hotel_name,
                                    'reservationItemId': reservation['reservationItemId']
                                })
                        else:
                            ready_data.append({
                            'address': address,
                            'image_url': img,
                            'full_name': full_name,
                            'start_date': start_date,
                            'end_date': end_date,
                            'room_name': room_name,
                            'price': total,
                            'conversation_id': conversation_id,
                            'cpce_id': cpce_id,
                            'hotel_name': hotel_name
                        })
        else:            
            months = 0
            months_next = 1
            count_months = 12 - int(datetime.datetime.now().strftime('%m'))
            
            for _ in range(count_months):
                now_date = datetime.datetime.now() + relativedelta(months=months)
                now_date = now_date.strftime('%Y-%m-%d')
                next_date = datetime.datetime.now() + relativedelta(months=months_next)
                next_date = next_date.strftime('%Y-%m-%d')
                
                json_data = {
                            'query': 'query getReservationsBySearchCriteria {reservationSearchV2(input: {propertyId: '+self.htid+', booked: true, bookingItemId: null, canceled: true, confirmationNumber: null, confirmed: true, startDate: "'+now_date+'", endDate: "'+next_date+'", dateType: \"checkIn\", evc: false, expediaCollect: true, timezoneOffset: \"+10:00\", firstName: null, hotelCollect: true, isSpecialRequest: false, isVIPBooking: false, lastName: null, reconciled: false, readyToReconcile: false, returnBookingItemIDsOnly: false, searchParam: null, unconfirmed: true searchForCancelWaiversOnly: false }) { reservationItems{ reservationItemId reservationInfo {reservationTpid propertyId startDate endDate createDateTime brandDisplayName newReservationItemId country reservationAttributes {businessModel bookingStatus fraudCancelled fraudReleased stayStatus eligibleForECNoShowAndCancel strongCustomerAuthentication invoiced} specialRequestDetails accessibilityRequestDetails product {productTypeId unitName bedTypeName propertyVipStatus} customerArrivalTime {arrival}readyToReconcile epsBooking } customer {id guestName phoneNumber email emailAlias country} loyaltyInfo {loyaltyStatus vipAmenities} confirmationInfo {productConfirmationCode} conversationsInfo {conversationsSupported id unreadMessageCount conversationStatus cpcePartnerId}totalAmounts {totalAmountForPartners {value currencyCode}totalCommissionAmount {value currencyCode}totalReservationAmount {value currencyCode}propertyBookingTotal {value currencyCode}totalReservationAmountInPartnerCurrency {value currencyCode}}reservationActions {requestToCancel {reason actionSupported actionUnsupportedBehavior {hide disable}}changeStayDates {reason actionSupported}requestRelocation {reason actionSupported}actionAttributes {highFence}reconciliationActions {markAsNoShow {reason actionSupported actionUnsupportedBehavior {hide disable openVa}virtualAgentParameters {intentName taxonomyId}}undoMarkNoShow {reason actionSupported actionUnsupportedBehavior {hide disable}}changeCancellationFee {reason actionSupported actionUnsupportedBehavior {hide disable}}resetCancellationFee {reason actionSupported actionUnsupportedBehavior {hide disable}}markAsCancellation {reason actionSupported actionUnsupportedBehavior {hide disable}}undoMarkAsCancellation {reason actionSupported actionUnsupportedBehavior {hide disable}}changeReservationAmountsOrDates {reason actionSupported actionUnsupportedBehavior {hide disable}}resetReservationAmountsOrDates {reason actionSupported actionUnsupportedBehavior {hide disable}}}}reconciliationInfo {reconciliationDateTime reconciliationType}paymentInfo {evcCardDetailsExist expediaVirtualCardResourceId creditCardDetails { viewable viewCountLimit viewCountLeft viewCount hideCvvFromDisplay valid prevalidateCardOptIn cardValidationViewable inViewingWindow validationInfo {validationStatus validationType validationDate validationBy hasGuestProvidedNewCC newCreditCardReceivedDate is24HoursFromLastValidation } }}billingInfo {invoiceNumber }cancellationInfo {cancelDateTime cancellationPolicy {priceCurrencyCode costCurrencyCode policyType cancellationPenalties {penaltyCost penaltyPrice penaltyPerStayFee penaltyTime penaltyInterval penaltyStartHour penaltyEndHour }nonrefundableDatesList}}compensationDetails {reservationWaiverType reservationFeeAmounts {propertyWaivedFeeLineItem {costCurrency costAmount }}} searchWaiverRequest {serviceRequestId type typeDetails state orderNumber partnerId createdDate srConversationId lastUpdatedDate notes {text author {firstName lastName }}}} numOfCancelWaivers}}',
                            'variables': {},
                        }

                response = await self.session.post(
                    'https://api.expediapartnercentral.com/supply/experience/gateway/graphql',
                    json=json_data,
                )
                reservations_raw = response.json()['data']['reservationSearchV2']['reservationItems']
                print(f'COUNT_RESERVATIONS -> {len(reservations_raw)}')
                for reservation in reservations_raw:
                    hotel_prop_id = reservation['reservationInfo']['propertyId']
                    hotel_info = hotels_info.get(hotel_prop_id, None)
                    
                    if hotel_info:
                        address = hotel_info['address']
                        img = hotel_info['img'],
                        hotel_name = hotel_info['hotel_name']
                    else:
                        hotel_info = await self.get_hotels_info(hotel_prop_id)
                        hotels_info[hotel_prop_id] = hotel_info
                        
                        address = hotel_info['address']
                        img = hotel_info['img']
                        hotel_name = hotel_info['hotel_name']
                    
                    full_name = reservation['customer']['guestName']
                    start_date = reservation['reservationInfo']['startDate']
                    end_date = reservation['reservationInfo']['endDate']
                    
                    price_data = reservation['totalAmounts']['totalReservationAmountInPartnerCurrency']
                    currency = price_data['currencyCode']
                    room_name = reservation['reservationInfo']['product']['unitName']
                    
                    total = await convert_to_eur(str(price_data['value']), currency, rate)
                    total, rate = total
                    
                    if reservation['conversationsInfo']['conversationsSupported']:
                        if reservation['reservationInfo']['reservationAttributes']['stayStatus'] != 'cancelled':
                            conversation_id = reservation['conversationsInfo']['id']
                            cpce_id = reservation['conversationsInfo']['cpcePartnerId']
                            
                            if not conversation_id:
                                not_create_chat.append({
                                    'address': address,
                                    'image_url': img,
                                    'full_name': full_name,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'room_name': room_name,
                                    'price': total,
                                    'conversation_id': conversation_id,
                                    'cpce_id': cpce_id,
                                    'hotel_name': hotel_name,
                                    'reservationItemId': reservation['reservationItemId']
                                })
                            else:
                                ready_data.append({
                                    'address': address,
                                    'image_url': img,
                                    'full_name': full_name,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'room_name': room_name,
                                    'price': total,
                                    'conversation_id': conversation_id,
                                    'cpce_id': cpce_id,
                                    'hotel_name': hotel_name,
                                    'reservationItemId': reservation['reservationItemId']
                                })

                months += 1
                months_next += 1
        
        print(f'READY DATA -> {len(ready_data)} NOT CREATE CHAT -> {len(not_create_chat)}')
        
        if not_create_chat:
            await message.answer('Создаём чаты для броней')
            futures = []
            
            for data in not_create_chat:
                futures.append(asyncio.create_task(self.create_chat(data)))

            for result in asyncio.as_completed(futures):
                result = await result
                print(result)
                if result:
                    ready_data.append(result)

            
        self.session.headers.pop('client-name')
        return ready_data
    
    
    async def get_hotels_info(self, prop_id):
        r = await self.session.get(f'https://apps.expediapartnercentral.com/supply/property/overview?propertyId={prop_id}')

        soup = bs(r.text, 'html.parser')
        
        img = soup.select('#content-home-basic-info > div > div > figure > div > img')[0].get('src')
        address = soup.findAll('div', attrs={'class': 'uitk-text uitk-text-spacing-three uitk-type-300 uitk-text-default-theme'})[0].get_text()
        hotel_name = soup.findAll('h4', attrs={'class': 'uitk-heading uitk-heading-4'})[0].get_text()
        
        return {'address': address, 'img': img, 'hotel_name': hotel_name}
    
    
    async def send_message(self, message, conversation_id, cpce_id):        
        json_data = {
            'conversationId': conversation_id,
            'cpcePartnerId': cpce_id,
            'body': message,
        }

        retry = 0
        
        while True:
            if retry == 10:
                return False
            
            response = await self.session.post(
                'https://apps.expediapartnercentral.com/lodging/conversations/api/conversations/sendMessage',
                json=json_data
            )
            
            print(response.text)
            if '"messageStatus":"DELIVERED"' in response.text:
                return True
            
            
            retry += 1
            await asyncio.sleep(random.uniform(1, 3))
    