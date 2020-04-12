Icon200='''
HTTP/1.0 200 OK
accept-ranges: bytes
content-type: image/x-icon
Access-Control-Allow-Origin: *
Server: ESP32-Webserver

'''

OK200 = '''
HTTP/1.0 200 OK
Content-Type: {0};charset=utf-8
Access-Control-Allow-Origin: *
Server: ESP32-Webserver

'''

NotFound404 = '''
HTTP/1.0 404 NOT FOUND
Content-Type: text/html;charset=utf-8
Access-Control-Allow-Origin: *
Server: ESP32-Webserver

<title>404 Not Found</title>
<h1>404 NOT FOUND   ):</h1><hr>
<a href="https://github.com/windfallw" style="text-decoration:none;">
Welcome to->MY GITHUB</a>
'''

dType = {
    'html': 'text/html',
    'css': 'text/css',
    'javascript': 'application/javascript',
    'json': 'application/json',
    'icon': 'image/x-icon'
}


def header200(tp='html'):
    for i in dType.keys():
        if tp == i:
            return OK200.format(dType[tp])
    return OK200.format(dType['html'])
