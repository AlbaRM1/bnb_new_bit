import base64


def base64CookieToJsonCookie(base64Cookie):
    encode_cookie = base64Cookie
    cookies = []
    for cookie in encode_cookie.split('\n'):
        try:
            coookie = list(cookie.split('\t'))
            json_cookie = {'domain': coookie[0], 'expirationDate': coookie[4], 'hostOnly': coookie[1], 'httpOnly': coookie[3],
                    'name': coookie[5].replace('\\', '\\\\').replace('"', '\\"'), 'path': coookie[2],
                    'value': coookie[6].replace('\\', '\\\\').replace('"', '\\"')}
            cookies.append(json_cookie)
        except:
            pass
    return cookies