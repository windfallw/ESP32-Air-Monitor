from py import Webserver, device
import _thread
import machine
import re

app = Webserver.WebServant(static_path='/src', template_path='/www')


@app.route('/')
def index(*arguments):
    client, address = arguments
    client.send(Webserver.header200())
    with open('www/index.html', 'rb') as f:
        line = f.read(8192)
        while line:
            client.send(line)
            line = f.read(8192)
        f.close()


@app.route('/sysinfo')
def infoair(*arguments):
    client, address = arguments
    client.send(Webserver.header200('json'))
    client.send(device.getSystemInfo(WiFi.NetworkInfo, [External_Device.uartCount, External_Device.uartFail]))


@app.route('/info/air')
def infoair(*arguments):
    client, address = arguments
    client.send(Webserver.header200('json'))
    client.send(External_Device.PMS7003)


@app.route('/info/gps')
def infogps(*arguments):
    client, address = arguments
    client.send(Webserver.header200('json'))
    client.send(External_Device.GPS)


@app.route('/info/voc')
def infogps(*arguments):
    client, address = arguments
    client.send(Webserver.header200('json'))
    client.send(External_Device.VOC)


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
        WiFi.connect_wifi(ssid, pwd)
        return
    if WiFi.connect_wifi(ssid, pwd):
        client.send("<p>成功连接到 %s </p>" % ssid)
        WiFi.save_wifi(ssid, pwd)
    else:
        client.send("<p>连接失败......你输入的密码是 %s</p>" % (pwd))


@app.route('/posthost', 'POST')
def posthost(*arguments):
    client, address, client_data = arguments
    client.send(Webserver.header200())
    client.send("<p>正在设置中......</p>")
    obj2 = re.match(r'Host=(.*?)&Port=(.*)', client_data)
    host, port = obj2.group(1), int(obj2.group(2))
    device.save_client(host, port)
    client.send("<p>设置完毕......已自动重启</p>")
    client.close()
    machine.reset()


if __name__ == '__main__':
    tim0 = machine.Timer(0)
    tim1 = machine.Timer(1)
    tim2 = machine.Timer(2)
    WiFi = device.WiFi()
    External_Device = device.External()

    # tim0.init(period=60000, mode=machine.Timer.PERIODIC,
    #           callback=lambda t: WiFi.check_wifi_disconnect())  # 检测WiFi是否断线,防止无限重连
    tim1.init(period=5000, mode=machine.Timer.PERIODIC,
              callback=lambda t: External_Device.DHT())  # 5秒读取一次dht
    tim2.init(period=1000, mode=machine.Timer.PERIODIC,
              callback=lambda t: External_Device.Screen(WiFi.NetworkInfo['station']['network']))  # 1秒刷新一次oled

    print(app.route_table_get, end='\n\n')
    print(app.route_table_post, end='\n\n')

    _thread.start_new_thread(app.run, ('0.0.0.0', 80))  # 多线程运行webserver
    _thread.start_new_thread(External_Device.UART2, ())  # 接受串口数据
