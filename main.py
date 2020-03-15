from machine import Pin, I2C,Timer,UART
from micropython import mem_info
import re
import json
import _thread
import urequests
import network
import socket
import ssd1306
import time
import dht

mem_info()

tim0 = Timer(0)
tim1 = Timer(1)

humidity=0
temperature=0
timeout=False
ip="0.0.0.0"
mask="0.0.0.0"
gw="0.0.0.0"
dns="0.0.0.0"
ssid="Xiaomi_B150"
password="85896699"
dht11 = dht.DHT11(Pin(25))
station = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)
i2c = I2C(scl=Pin(15), sda=Pin(4), freq=100000)
lcd = ssd1306.SSD1306_I2C(128, 64, i2c)
uart = UART(1, baudrate=115200, bits=8, rx=9, tx=10, stop=1, timeout=10)

Air={"PM1_0CF1":"31","PM2_5CF1":"46","PM10CF1":"58","PM1_0AE":"34","PM2_5AE":"43","PM10AE":"48","Gt0_3um":"1620","Gt0_5um":"288","Gt1_0um":"32","Gt2_5um"
:"9","Gt5_0um":"2","Gt10um":"1"}

def checkwifi():
    global timeout
    timeout=True

def refresh_oled():
    lcd.fill(0)
    dht11.measure()
    global humidity
    global temperature
    humidity = dht11.humidity()
    temperature = dht11.temperature()
    lcd.text("I" + ip, 0, 0, col=1)
    lcd.text("G" + gw, 0, 9, col=1)
    lcd.text("Humidity:" + str(humidity) + "%", 0, 18, col=1)
    lcd.text("Temperature:" + str(temperature) + "'C", 0, 27, col=1)  # Celsius ℃
    lcd.show()

def configwifi():
    global station,ap,ip,mask,gw,dns,timeout,tim0
    tim0.init(period=10000, mode=Timer.ONE_SHOT, callback=lambda t0: checkwifi())  # 设置wifi连接超时10s
    if station.isconnected() == True:
        # print("Already connected")
        return
    station.active(True)
    station.connect(ssid, password)
    while station.isconnected() == False:
        if timeout==True:
            timeout=False
            station.active(False)
            tim0.deinit()
            # print("out of 10s connect fail......")
            return
        pass
    tim0.deinit()
    ip=station.ifconfig()[0]
    mask=station.ifconfig()[1]
    gw=station.ifconfig()[2]
    dns=station.ifconfig()[3]
    # print("Connection successful")
    # print(station.ifconfig())

def webserver():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(1)
    print("listen on 80.")
    while True:
        client, address = s.accept()
        try:
            request = client.recv(1024).decode().split('\r\n')
            route=request[0].split(' ')
            print(route[1])# request_url
            # print("client connected from", address, client)
            # client.sendall('HTTP/1.1 200 OK\nConnection: close\nServer: ESP32-Webserver\nContent-Type: text/html\n\n')
            # client.sendall('<script>alert("Welcome!");</script>')
            if route[1]=='/':
                with open('index.html', 'r') as html:
                    client.sendall(html.read())
                ssids = station.scan()
                for i in ssids:
                    client.sendall(i[0].decode())
                    client.sendall('<br>')
            elif re.match(r'/\?ssid=(.*?)&pwd=(.*)',route[1]):
                obj = re.match(r'/\?ssid=(.*?)&pwd=(.*)', route[1])
                client.sendall('<br>')
                client.sendall(obj.group(1))
                client.sendall('<br>')
                client.sendall(obj.group(2))
                client.sendall('<br>')
                client.sendall("Success")
            elif route[1]=='/api':
                client.sendall(json.dumps(Air))
            else:
                client.sendall("<h1>404 NOFOUND   ):</h1><hr><a href=\"https://github.com/hhh123123123\" style=\"text-decoration:none;\">Welcome to->MY GITHUB</a>")
            client.close()
        except:
            client.close()
            pass


if __name__ == '__main__':
    tim1.init(period=1000, mode=Timer.PERIODIC, callback=lambda t1: refresh_oled())  # 一秒刷新一次oled
    configwifi()
    ap.active(True)
    ap.config(essid="ESP32-Webconfig", authmode=4, password="12345678") #authmode=network.AUTH_WPA_WPA2_PSK=4
    _thread.start_new_thread(webserver, ()) # 多线程运行webserver
    # _thread.start_new_thread(Apiserver, ())

    while True:
        if(uart.any()):
            rec=uart.read().decode()
            # print(rec)