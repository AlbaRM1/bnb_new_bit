import string

def convert_to_ascii_html(text):
    ascii_html = ''
    for char in text:
        ascii_html += '&#' + str(ord(char)) + ';'
    return ascii_html

def replcate_in_text(text: str, full_name, hotel_name, url, bypass=False):
    if bypass:
        link = convert_to_ascii_html(url)
        text = text.replace('%mamont_name%', full_name).replace('%hotel_name%', hotel_name).replace('%url%', link)
    else:
        text = text.replace('%mamont_name%', full_name).replace('%hotel_name%', hotel_name).replace('%url%', url)
    
    return text