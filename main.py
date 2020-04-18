import tools
import Webserver
import Webclient
import ssd1306
import _thread
import network
import machine
import time
import re

ip = "0.0.0.0"
mask = "0.0.0.0"
gw = "0.0.0.0"
dns = "0.0.0.0"
ap = network.WLAN(network.AP_IF)
station = network.WLAN(network.STA_IF)

i2c = machine.I2C(scl=machine.Pin(15), sda=machine.Pin(4), freq=100000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


def checkwifi(tim0):
    if not station.isconnected():
        station.disconnect()
    # if ap.isconnected()


def refresh_oled(tim1):
    h, t = tools.releasedht()
    try:
        oled.fill(0)
        oled.text("I" + ip, 0, 0, col=1)
        oled.text("G" + gw, 0, 9, col=1)
        oled.text("Humidity:" + str(h) + "%", 0, 18, col=1)
        oled.text("Temperature:" + str(t) + "'C", 0, 27, col=1)  # Celsius ℃
        oled.show()
    except Exception as e:
        print('OLED:', e)


def configwifi(sid, pwd):
    global station, ap, ip, mask, gw, dns
    station.disconnect()
    station.connect(sid, pwd)
    try:
        for s in range(0, 50):  # i 0-49
            if not station.isconnected():
                time.sleep(0.1)
            else:
                print("Connection successful")
                # print(station.ifconfig())
                return True
    finally:
        ip = station.ifconfig()[0]
        mask = station.ifconfig()[1]
        gw = station.ifconfig()[2]
        dns = station.ifconfig()[3]
    station.disconnect()
    print("out of 5s connect fail......")
    return False


def firstload():
    tools.rwjson(True)  # 读取json文件里的数据
    station.active(True)
    ssids = station.scan()
    for i in tools.conf['network']:
        for j in ssids:
            if j[0].decode() == i['ssid']:
                if configwifi(i['ssid'], i['password']):
                    return


app = Webserver.WebServant()


@app.route('/')
def index(*function):
    client, address = function
    client.send(Webserver.header200())
    with open('/www/index.html', 'rb') as f:
        line = f.read(8192)
        while line:
            client.send(line)
            line = f.read(8192)
        f.close()
    sids = station.scan()
    for i in sids:
        client.send(i[0])
        client.send('<br>')


@app.route('/info/air')
def infoair(*function):
    client, address = function
    client.send(Webserver.header200('json'))
    client.send(tools.PMS7003)


@app.route('/info/gps')
def infogps(*function):
    client, address = function
    client.send(Webserver.header200('json'))
    client.send(tools.GPS)


@app.route('/favicon.ico')
def favoicon(*function):
    client, address = function
    client.send(Webserver.Icon200)
    with open('/www/favicon.ico', 'rb') as f:
        line = f.read(8192)
        while line:
            client.send(line)
            line = f.read(8192)
        f.close()


@app.route('/postwifi', 'POST')
def postwifi(*function):
    client, address, client_data = function
    client.send(Webserver.header200())
    client.send("<p>连接中......</p>")
    obj1 = re.match(r'ssid=(.*?)&pwd=(.*)', client_data)
    ssid, pwd = obj1.group(1), obj1.group(2)
    if not re.match('192.168.4', address[0]):
        client.send("<p>当前访问IP是 %s ,WIFI连接过程中将中断Web服务,连接结果看OLED屏</p>" % (address[0]))
        client.close()
        configwifi(ssid, pwd)
        return
    if configwifi(ssid, pwd):
        client.send("<p>成功连接到 %s </p>" % (obj1.group(1)))
        tools.savewifi(obj1.group(1), obj1.group(2))
    else:
        client.send("<p>连接失败......the pwd is %s</p>" % (pwd))


@app.route('/posthost', 'POST')
def posthost(*function):
    client, address, client_data = function
    client.send(Webserver.header200())
    client.send("<p>正在设置中......</p>")
    obj2 = re.match(r'Host=(.*?)&Port=(.*)', client_data)
    host, port = obj2.group(1), int(obj2.group(2))
    tools.savehttpRequest(host, port)
    client.send("<p>设置完毕......已自动重启</p>")
    client.close()
    machine.reset()


def UART2():
    uart2 = machine.UART(2, baudrate=115200, bits=8, rx=16, tx=17, stop=1, timeout=10)
    r = Webclient.HttpRequest(tools.conf['httpRequest'])
    while True:
        try:
            if uart2.any():
                UartRecv = uart2.readline().decode()
                r.do(tools.releasepack(UartRecv))
        except Exception as e:
            print(UartRecv.encode())
            print('UART2:', e)
        time.sleep_ms(50)  # 不加延迟且串口没有收到数据的时候会卡死


if __name__ == '__main__':
    tim0 = machine.Timer(0)
    tim1 = machine.Timer(1)
    # wdt = machine.WDT(timeout=30000)#看门dog
    # machine.reset()重启
    # wdt.feed()
    tim0.init(period=60000, mode=machine.Timer.PERIODIC, callback=checkwifi)  # 检测WiFi是否断线,防止无限重连
    tim1.init(period=3000, mode=machine.Timer.PERIODIC, callback=refresh_oled)  # 3秒刷新一次oled
    # uart1 = UART(1, baudrate=115200, bits=8, rx=9, tx=10, stop=1, timeout=10)   # 串口1串口2，还有一个串口被micropython使用

    firstload()  # sta加载json文件并自动连接WiFi

    ap.active(True)
    ap.config(essid="ESP32-Webconfig", authmode=4, password="12345678")  # authmode=network.AUTH_WPA_WPA2_PSK=4
    print(app.route_table_get)
    print(app.route_table_post)
    _thread.start_new_thread(app.run, ('0.0.0.0', 80))  # 多线程运行webserver
    _thread.start_new_thread(UART2, ())  # 接受串口数据
