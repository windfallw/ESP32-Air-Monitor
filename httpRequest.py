import socket
import json
import gc


class Requester:
    RequestHeaders = '''
{0} {1} HTTP/1.1
host: {2}
Content-Type: application/json
cache-control: no-cache
content-length: {3}

'''
    url = 'https://www.example.com/info/sendair'
    method = 'POST'
    host = 'www.example.com'
    Path = {'pms7003': '/info/sendair', 'gps': '/info/sendgps'}
    Proto = 'http'
    Port = 80

    def __init__(self,conf):
        self.host=conf['host']
        self.Proto=conf['Proto']
        self.Port=conf['Port']
        self.method=conf['method']
        self.Path=conf['Path']

    def do(self, rec):
        # You must use getaddrinfo() even for numeric addresses 您必须使用getaddrinfo()，即使是用于数字型地址
        # [(2, 1, 0, 'www.example.com', ('12.34.56.78', 80))](family, type, proto, canonname, sockaddr)
        try:
            sockinfo = socket.getaddrinfo(self.host, self.Port)[0]
            s = socket.socket(sockinfo[0], sockinfo[1], sockinfo[2])

            t = rec['type']
            if t == 'pms7003' or t == 'gps':
                rec = json.dumps(rec)
                rh = self.RequestHeaders.format(self.method, self.Path[t], self.host, len(rec))
            else:
                return None

            s.settimeout(10)
            s.connect(sockinfo[-1])
            #https占用资源巨大慎用
            if self.Proto == 'https':
                import ssl
                s = ssl.wrap_socket(s)
            s.write(rh)
            s.write(rec)
            # print(s.readline())
            # while True:
            #     h = s.readline()
            #     if h == b"" or h == b"\r\n":
            #         break
            #     print(h.decode())
        except Exception as e:
            print('Requester:',e)
        finally:
            s.close()
            gc.collect()
