import tools
import Webserver
import Webclient
import _thread
import machine
import time
import re

app = Webserver.WebServant(static_path='/src', template_path='/www')


@app.route('/')
def index(*arguments):
    client, address = arguments
    client.send(Webserver.header200())
    with open('/www/index.html', 'rb') as f:
        line = f.read(8192)
        while line:
            client.send(line)
            line = f.read(8192)
        f.close()
    # sids = station.scan()
    # for i in sids:
    #     client.send(i[0])
    #     client.send('<br>')


@app.route('/info/air')
def infoair(*arguments):
    client, address = arguments
    client.send(Webserver.header200('json'))
    client.send(tools.PMS7003)


@app.route('/info/gps')
def infogps(*arguments):
    client, address = arguments
    client.send(Webserver.header200('json'))
    client.send(tools.GPS)


@app.route('/favicon.ico')
def favoicon(*arguments):
    client, address = arguments
    client.send(Webserver.Icon200)
    with open('/www/favicon.ico', 'rb') as f:
        line = f.read(8192)
        while line:
            client.send(line)
            line = f.read(8192)
        f.close()


@app.route('/postwifi', 'POST')
def postwifi(*arguments):
    client, address, client_data = arguments
    client.send(Webserver.header200())
    client.send("<p>连接中......</p>")
    obj1 = re.match(r'ssid=(.*?)&pwd=(.*)', client_data)
    ssid, pwd = obj1.group(1), obj1.group(2)
    if not re.match('192.168.4', address[0]):
        client.send("<p>当前访问IP是 %s ,WIFI连接过程中将中断Web服务,连接结果看OLED屏</p>" % (address[0]))
        client.close()
        wifi_manage.connect_wifi(ssid, pwd)
        return
    if wifi_manage.connect_wifi(ssid, pwd):
        client.send("<p>成功连接到 %s </p>" % ssid)
        wifi_manage.save_wifi_config(ssid, pwd)
    else:
        client.send("<p>连接失败......你输入的密码是 %s</p>" % (pwd))


@app.route('/posthost', 'POST')
def posthost(*arguments):
    client, address, client_data = arguments
    client.send(Webserver.header200())
    client.send("<p>正在设置中......</p>")
    obj2 = re.match(r'Host=(.*?)&Port=(.*)', client_data)
    host, port = obj2.group(1), int(obj2.group(2))
    tools.save_client_config(host, port)
    client.send("<p>设置完毕......已自动重启</p>")
    client.close()
    machine.reset()


def UART2():
    uart2 = machine.UART(2, baudrate=115200, bits=8, rx=16, tx=17, stop=1, timeout=10)
    while True:
        try:
            if uart2.any():
                UartRecv = uart2.readline().decode()
                request.send_json(devices_manage.pack(UartRecv))
        except Exception as e:
            print('UART2:', e)
        time.sleep_ms(50)  # 不加延迟且串口没有收到数据的时候会卡死


if __name__ == '__main__':
    wifi_manage = tools.WiFi()
    devices_manage = tools.devices()
    wifi_manage.tim0.init(period=60000, mode=machine.Timer.PERIODIC,
                          callback=lambda t: wifi_manage.check_wifi_disconnect())  # 检测WiFi是否断线,防止无限重连
    devices_manage.tim1.init(period=5000, mode=machine.Timer.PERIODIC,
                             callback=lambda t: devices_manage.release_dht())  # 5秒读取一次dht
    devices_manage.tim2.init(period=1000, mode=machine.Timer.PERIODIC,
                             callback=lambda t: devices_manage.refresh_screen(wifi_manage.network_config))  # 1秒刷新一次oled
    request = Webclient.HttpRequest(tools.config['client_config'])

    print(app.route_table_get)
    print(app.route_table_post)
    _thread.start_new_thread(app.run, ('0.0.0.0', 80))  # 多线程运行webserver
    _thread.start_new_thread(UART2, ())  # 接受串口数据
