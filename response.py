
OK200 = '''
HTTP/1.1 200 OK
Content-Type: {0};charset=utf-8
Access-Control-Allow-Origin: *
Server: ESP32-Webserver

'''

NotFound404 = '''
HTTP/1.1 404 NOT FOUND
Content-Type: {0};charset=utf-8
Access-Control-Allow-Origin: *
Server: ESP32-Webserver

<title>404 Not Found</title>
<h1>404 NOT FOUND   ):</h1><hr>
<a href="https://github.com/hhh123123123" style="text-decoration:none;">
Welcome to->MY GITHUB</a>
'''

dType={
    'html':'text/html',
    'css':'text/css',
    'javascript':'application/javascript',
    'json':'application/json',
}


def header200(tp='html'):
    for i in dType.keys():
        if tp==i:
            return OK200.format(dType[tp])
        else:
            return OK200.format(dType['html'])


def header404(tp='html'):
    for i in dType.keys():
        if tp==i:
            return NotFound404.format(dType[tp])
        else:
            return NotFound404.format(dType['html'])