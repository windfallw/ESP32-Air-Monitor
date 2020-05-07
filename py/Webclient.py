import socket
import gc


class HttpRequest:
    RequestHeader_template = '''
{0} {1} HTTP/1.1
host: {2}
Content-Type: application/json
cache-control: no-cache
content-length: {3}

'''
    # url = 'https://www.example.com/info/sendair'
    method = 'POST'
    proto = 'http'
    host = 'www.example.com'
    port = 80
    sockinfotmp = ()  # 暂存域名解析信息，防止域名解析失败后无法建立请求
    requestCount = 0
    requestSuccess = 0

    def __init__(self, config):
        self.method = config['method']
        self.proto = config['proto']
        self.host = config['host']
        self.port = config['port']

    def send_json(self, data, path):
        # You must use getaddrinfo() even for numeric addresses 您必须使用getaddrinfo()，即使是用于数字型地址
        # [(2, 1, 0, 'www.example.com', ('12.34.56.78', 80))](family, type, proto, canonname, sockaddr)
        try:
            self.requestCount += 1
            try:
                sockinfo = socket.getaddrinfo(self.host, self.port)[0]
                self.sockinfotmp = sockinfo
            except IndexError:
                sockinfo = self.sockinfotmp
            s = socket.socket(sockinfo[0], sockinfo[1], sockinfo[2])
            RequestHeader = self.RequestHeader_template.format(self.method, path, self.host, len(data))
            s.settimeout(10)
            s.connect(sockinfo[-1])
            # https占用资源巨大慎用
            if self.proto == 'https':
                import ssl
                s = ssl.wrap_socket(s)
            s.write(RequestHeader)
            s.write(data)
            while True:
                line = s.readline()
                if line == b"" or line == b"\r\n":
                    break
                elif line == b'HTTP/1.1 200 OK\r\n':
                    self.requestSuccess += 1
                    # print(line)
            s.close()
        except Exception as e:
            print('WebClient:', e)
        finally:
            gc.collect()
