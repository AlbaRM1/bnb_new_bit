import json
import re
import httpx
from iso3166 import countries
from countryinfo import CountryInfo


async def convert_to_eur(value, currency):    
    total_raw = value.replace('\xa0', '')
    print(total_raw)
    
    if ',' in total_raw:
        total_raw = total_raw.replace(',', '')

    total = re.findall(r'[\d\.\d]+', total_raw)
    if total[0] == '.':
        total = total[1]
    else:
        total = total[0]


    symbol = total_raw.replace(total, '')
    print(symbol)
    
    total = total.strip()    
    total = round(float(total), 2)
    
    symbol_name = currency

    
    async with httpx.AsyncClient(timeout=60) as client:
        response_json = await client.get(f'https://open.er-api.com/v6/latest/{symbol_name}')
        response_json = response_json.json()
        
        rate = response_json['rates']['EUR']

        total = total * float(rate)
        total = round(total, 2)
    return total