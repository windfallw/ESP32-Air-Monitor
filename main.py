from py import Webserver, device
import _thread
import machine
import time
import re

app = Webserver.WebServant(static_path='/src', template_path='/www')
WiFi = device.WiFi()
External_Device = device.External()


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
def sysinfo(*arguments):
    client, address = arguments
    client.send(Webserver.header200('json'))
    client.send(device.getSystemInfo(WiFi.NetworkInfo, [External_Device.uartCount, External_Device.uartSuccess]))


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
def infovoc(*arguments):
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


@app.route('/machine', 'post')
def machineCtl(*arguments):
    client, address, client_data = arguments
    if client_data == 'reset':
        client.send(Webserver.header200('text'))
        client.send(client_data)
        client.close()
        machine.reset()
    elif client_data == 'scan':
        client.send(Webserver.header200('text'))
        client.send(client_data)
        client.close()
        WiFi.RefreshWiFiList = True
    else:
        client.send(Webserver.BadRequest400)


@app.route('/postwifi', 'POST')
def postwifi(*arguments):
    client, address, client_data = arguments
    client.send(Webserver.header200('text'))
    client.send("正在连接中......")
    obj1 = re.match(r'ssid=(.*?)&pwd=(.*)', client_data)
    ssid, pwd = obj1.group(1), obj1.group(2)
    if not re.match('192.168.4', address[0]):
        client.send("当前访问IP是 %s,WIFI连接过程中将中断Web服务,连接结果请看OLED屏或web是否刷新" % (address[0]))
        client.close()
        WiFi.ConnectWiFi(ssid, pwd)
        return
    if WiFi.ConnectWiFi(ssid, pwd):
        client.send("成功连接到 %s" % ssid)
        WiFi.SaveWiFi(ssid, pwd)
    else:
        client.send("连接失败你输入的密码是 %s" % (pwd))


@app.route('/posthost', 'POST')
def posthost(*arguments):
    client, address, client_data = arguments
    client.send(Webserver.header200('text'))
    client.send("正在设置中......")
    obj2 = re.match(r'Host=(.*?)&Port=(.*)', client_data)
    host, port = obj2.group(1), int(obj2.group(2))
    device.save_client(host, port)
    client.send("设置完毕下次重启生效")
    client.close()


def Refresh():
    while True:
        if External_Device.RefreshDHT:
            External_Device.RefreshDHT = False
            External_Device.DHT()
        if External_Device.RefreshOLED:
            External_Device.RefreshOLED = False
            External_Device.Screen(WiFi.NetworkInfo['station']['network'])
        if WiFi.RefreshWiFiStatus:
            WiFi.RefreshWiFiStatus = False
            WiFi.WiFiStatus()
            if WiFi.station.status() not in [1001, 1010]:
                print('WiFiStatus:', WiFi.station.status())
                WiFi.loadExistWiFi()
        if WiFi.RefreshWiFiList:
            WiFi.RefreshWiFiList = False
            WiFi.ScanWiFi()
        time.sleep_ms(50)  # 找点事做防止线程卡死循环


if __name__ == '__main__':
    tim0 = machine.Timer(0)
    tim1 = machine.Timer(1)
    tim2 = machine.Timer(2)
    # tim3 = machine.Timer(3)

    tim0.init(period=10000, mode=machine.Timer.PERIODIC,
              callback=lambda t: WiFi.interruptWiFi())  # 10秒读取一次WiFi状态,断线自动重连
    tim1.init(period=5000, mode=machine.Timer.PERIODIC,
              callback=lambda t: External_Device.interruptDHT())  # 5秒读取一次dht
    tim2.init(period=1000, mode=machine.Timer.PERIODIC,
              callback=lambda t: External_Device.interruptOLED())  # 1秒刷新一次OLED

    print(app.route_table_get)
    print(app.route_table_post)

    _thread.start_new_thread(app.run, ('0.0.0.0', 80))  # 多线程运行WebServer
    _thread.start_new_thread(External_Device.UART2, ())  # 接受串口数据并打包发送到服务器
    _thread.start_new_thread(Refresh, ())  # 检测定时器到期并执行相应操作
