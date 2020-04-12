import tools
import httpResponse
import httpRequest
import ssd1306
import _thread
import network
import socket
import machine
import time
import gc
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
    for i in tools.conf['Sid_Pwd']:
        for j in ssids:
            if j[0].decode() == i['ssid']:
                if configwifi(i['ssid'], i['password']):
                    return


def Webserver():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(1)
    print("listen on 80.")
    while True:
        try:
            client, address = s.accept()
            request = client.recv(1024).decode().split('\r\n', 1)
            route = request[0].split(' ', 2)
            # print(request)
            # print(route)
            print(address, client)
            print(route[1])  # request_url

            if route[0].upper() == 'POST':
                postdata = request[1].rsplit('\r\n', 1)[-1]
                print(postdata)

                if route[1] == '/postwifi':
                    client.send(httpResponse.header200())
                    client.send("<p>连接中......</p>")
                    obj1 = re.match(r'ssid=(.*?)&pwd=(.*)', postdata)
                    ssid, pwd = obj1.group(1), obj1.group(2)
                    if not re.match('192.168.4', address[0]):
                        client.send("<p>当前访问IP是 %s ,WIFI连接过程中将中断Web通信,连接结果看OLED屏</p>" % (address[0]))
                        client.close()
                        configwifi(ssid, pwd)
                        continue
                    if configwifi(ssid, pwd):
                        client.send("<p>成功连接到 %s </p>" % (obj1.group(1)))
                        tools.savewifi(obj1.group(1), obj1.group(2))
                    else:
                        client.send("<p>连接失败......the pwd is %s</p>" % (pwd))

                if route[1] == '/posthost':
                    client.send(httpResponse.header200())
                    client.send("<p>正在设置中......</p>")
                    obj2 = re.match(r'Host=(.*?)&Port=(.*)', postdata)
                    host, port = obj2.group(1), int(obj2.group(2))
                    tools.saverequester(host, port)
                    client.send("<p>设置完毕......已自动重启</p>")
                    client.close()
                    machine.reset()

            elif route[0].upper() == 'GET':

                if route[1] == '/':
                    client.send(httpResponse.header200())
                    with open('/www/index.html', 'rb') as html:
                        client.send(html.read())
                    sids = station.scan()
                    for i in sids:
                        client.send(i[0])
                        client.send('<br>')

                elif route[1] == '/info/air':
                    client.send(httpResponse.header200('json'))
                    client.send(tools.String_Air)

                elif route[1] == '/info/gps':
                    client.send(httpResponse.header200('json'))
                    client.send(tools.String_GPS)

                elif route[1] == '/favicon.ico':
                    client.send(httpResponse.Icon200)
                    with open('/www/favicon.ico', 'rb') as f:
                        line = f.read(8192)
                        while line:
                            client.send(line)
                            line = f.read(8192)
                        f.close()

                elif route[1] == '/src/bootstrap.min.css':
                    client.send(httpResponse.header200('css'))
                    with open('/src/bootstrap.min.css', 'rb') as f:
                        line = f.read(8192)
                        while line:
                            client.send(line)
                            line = f.read(8192)
                        f.close()

                elif route[1] == '/src/bootstrap.bundle.min.js':
                    client.send(httpResponse.header200('javascript'))
                    with open('/src/bootstrap.bundle.min.js', 'rb') as f:
                        line = f.read(8192)
                        while line:
                            client.send(line)
                            line = f.read(8192)
                        f.close()

                elif route[1] == '/src/echarts.min.js':
                    client.send(httpResponse.header200('javascript'))
                    with open('/src/echarts.min.js', 'rb') as f:
                        line = f.read(8192)
                        while line:
                            client.send(line)
                            line = f.read(8192)
                        f.close()

                elif route[1] == '/src/jquery.min.js':
                    client.send(httpResponse.header200('javascript'))
                    with open('/src/jquery.min.js', 'rb') as f:
                        line = f.read(8192)
                        while line:
                            client.send(line)
                            line = f.read(8192)
                        f.close()

            else:
                client.send(httpResponse.NotFound404)

        except Exception as e:
            print('WEBSrv:', e)

        finally:
            client.close()
            gc.collect()
            print('use:', gc.mem_alloc(), 'remain:', gc.mem_free())


def UART2():
    r = httpRequest.Requester(tools.conf['Requester'])
    while True:
        try:
            if (uart2.any()):
                rec = uart2.readline().decode()
                r.do(tools.releasepack(rec))
        except Exception as e:
            print(rec.encode())
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
    uart2 = machine.UART(2, baudrate=115200, bits=8, rx=16, tx=17, stop=1, timeout=10)

    firstload()  # sta加载json文件并自动连接WiFi

    ap.active(True)
    ap.config(essid="ESP32-Webconfig", authmode=4, password="12345678")  # authmode=network.AUTH_WPA_WPA2_PSK=4

    _thread.start_new_thread(Webserver, ())  # 多线程运行webserver
    _thread.start_new_thread(UART2, ())  # 接受串口数据
