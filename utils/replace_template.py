import string


def replcate_in_text(text: str, full_name, hotel_name, url, bypass=False):
    if bypass:
        url = url.replace(' ', '')
        url = f'[// Click //](//guest@{url})'
        text = text.replace('%mamont_name%', full_name).replace('%hotel_name%', hotel_name).replace('%url%', url)
    else:
        text = text.replace('%mamont_name%', full_name).replace('%hotel_name%', hotel_name).replace('%url%', url)
    
    return text