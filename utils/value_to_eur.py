import json
import re
import httpx
from iso3166 import countries
from countryinfo import CountryInfo

async def convert_to_eur(value, country):
    currencies = json.load(open('currencies.json', 'r', encoding='utf-8', errors='ignore'))["currencies"]
    
    total_raw = value.replace('\xa0', '')
    print(total_raw)
    
    if ',' in total_raw:
        total_raw = total_raw.replace(',', '')

    total = re.findall(r'[\d\.\d]+', total_raw)[0]
    symbol = total_raw.replace(total, '')
    print(symbol)
    
    
    if country == 'com' and symbol == '$':
        symbol_name = 'usd'
    elif country == 'com' and symbol != '$':
        for i in currencies:
            if symbol == i['symbol_native'] or symbol == i['symbol']:
                symbol_name = i['code'].lower()
    else:
        country_name = countries.get(country)[0]
        symbol_name = CountryInfo(country_name).currencies()[0].lower()
    
    total = total.strip()    
    total = round(float(total), 2)
    
    async with httpx.AsyncClient(timeout=60) as client:
        response_json = await client.get(f'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{symbol_name}.json')
        response_json = response_json.json()
        
        rate = response_json[symbol_name]['eur']

        total = total * float(rate)
        total = round(total, 2)
    return total