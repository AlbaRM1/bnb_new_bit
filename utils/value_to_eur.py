import json
import re
import httpx

def convert_to_eur(value):
    currencies = json.load(open('currencies.json', 'r', encoding='utf-8', errors='ignore'))["currencies"]
    
    total_raw = value.replace('\xa0', '')
    print(total_raw)
    
    if ',' in total_raw:
        total_raw = total_raw.replace(',', '')
    
    total = re.findall(r'[\d\.\d]+', total_raw)[0]
    symbol = total_raw.replace(total, '')
    print(symbol)
    
    for i in currencies:
        if symbol == i['symbol_native'] or symbol == i['symbol']:
            symbol_name = i['code'].lower()
    
    total = total.strip()    
    total = round(float(total), 2)
    
    response_json = httpx.get(f'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{symbol_name}.json').json()
    rate = response_json[symbol_name]['eur']

    total = total * float(rate)
    total = round(total, 2)
    return total