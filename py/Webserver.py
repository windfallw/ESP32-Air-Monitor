import socket
import os
import gc

Icon200 = '''
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

BadRequest400 = '''
HTTP/1.0 400 Bad Request
Content-Type: text/html;charset=utf-8
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

MethodNotAllowed405 = '''
HTTP/1.0 405 Method Not Allowed
Content-Type: text/html;charset=utf-8
Access-Control-Allow-Origin: *
Server: ESP32-Webserver

'''

data_type = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'application/javascript',
    'json': 'application/json',
    'ico': 'image/x-icon',
    'text': 'text/plain'
}


def header200(data_type_key='html'):
    """传入响应头的文件类型"""
    for i in data_type.keys():
        if data_type_key == i:
            return OK200.format(data_type[data_type_key])
    return OK200.format(data_type['html'])


class WebServant:
    route_table_get = []
    route_table_post = []
    autoload_allow_staticfiletype = ['js', 'css']

    def __init__(self, static_path=None, template_path=None):
        """
        init初始化时可自动添加指定目录下的html或js css文件在get路由表中, 指定目录请使用绝对路径.
        static_path文件夹中请放js和css,template_path放html.
        """
        if static_path:
            os.chdir(static_path)
            static_file = os.listdir()
            for i in static_file:
                type = i.rsplit('.')[-1]
                if type not in self.autoload_allow_staticfiletype:
                    continue
                file_path = static_path + '/' + i
                self.add_file_to_route(file_path, file_path, type)

        if template_path:
            os.chdir('..' + template_path)
            template_file = os.listdir()
            for i in template_file:
                type = i.rsplit('.')[-1]
                if type == 'html':
                    file_path = template_path + '/' + i
                    route_path = '/' + i
                    self.add_file_to_route(file_path, route_path, type)

        os.chdir('/')  # 读取完文件后必须回到根目录否则main.py的函数无法正常加载
        gc.collect()

    def add_file_to_route(self, file_path, route_path, type):
        """此函数可以直接将指定文件添加到路由表里，但你应当在init初始化里完成"""

        def file_function(*arguments, p=file_path, t=type):
            client, address = arguments
            client.send(header200(t))
            with open(p, 'rb') as f:
                line = f.read(8192)
                while line:
                    client.send(line)
                    line = f.read(8192)
                f.close()
            client.close()

        self.route_table_get.append([route_path, file_function])

    def route(self, path, method='GET'):
        """装饰器,方法可选择get或者post,默认为get"""

        def decorator(func):
            if method.upper() == 'GET':
                self.route_table_get.append([path, func])
            elif method.upper() == 'POST':
                self.route_table_post.append([path, func])
            else:
                raise Exception("unsupported method!", method)
            return func

        return decorator

    def run(self, host='0.0.0.0', port=80):
        """host和port默认为本机ip的80端口"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(5)
        print("listen on %s." % port)
        while True:
            try:
                client, address = sock.accept()
                request_head, request_data = client.recv(1024).decode().split('\r\n', 1)  # 处理http请求头分割成请求部分和数据部分
                request_method, request_url, request_version = request_head.split(' ', 2)  # 将请求方法 请求路径 http版本分割出来
                client_data = request_data.rsplit('\r\n', 1)[-1]  # 用户发送的数据
                # print(request_url, request_method, address)
                flag = False
                if request_method.upper() == 'GET':
                    for i in self.route_table_get:
                        path, func = i
                        if path == request_url:
                            func(client, address)
                            flag = True
                            break
                    if not flag:
                        client.send(NotFound404)
                elif request_method.upper() == 'POST':
                    for i in self.route_table_post:
                        path, func = i
                        if path == request_url:
                            func(client, address, client_data)
                            flag = True
                            break
                    if not flag:
                        client.send(NotFound404)
                else:
                    client.send(MethodNotAllowed405)
                client.close()
            except Exception as e:
                print('WebServant:', e)
            finally:
                gc.collect()
