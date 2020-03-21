from machine import Pin, I2C,Timer,UART
from micropython import mem_info
import urequests
import _thread
import network
import socket
import ssd1306
import json
import time
import dht
import re

mem_info()

ip="0.0.0.0"
mask="0.0.0.0"
gw="0.0.0.0"
dns="0.0.0.0"
timeout=False
ap = network.WLAN(network.AP_IF)
station = network.WLAN(network.STA_IF)

humidity=0
temperature=0
dht11 = dht.DHT11(Pin(25))

i2c = I2C(scl=Pin(15), sda=Pin(4), freq=100000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


jsondoc={
    'Sid_Pwd':[{'ssid':"example",'password':'yourpassword'}]
}

Air={"PM1_0CF1":"31","PM2_5CF1":"46","PM10CF1":"58","PM1_0AE":"34","PM2_5AE":"43","PM10AE":"48","Gt0_3um":"1620","Gt0_5um":"288","Gt1_0um":"32","Gt2_5um"
:"9","Gt5_0um":"2","Gt10um":"1"}

def checkwifi(tim0):
    if not station.isconnected():
        station.disconnect()

def refresh_oled(tim1):
    oled.fill(0)
    dht11.measure()
    global humidity
    global temperature
    humidity = dht11.humidity()
    temperature = dht11.temperature()
    oled.text("I" + ip, 0, 0, col=1)
    oled.text("G" + gw, 0, 9, col=1)
    oled.text("Humidity:" + str(humidity) + "%", 0, 18, col=1)
    oled.text("Temperature:" + str(temperature) + "'C", 0, 27, col=1)  # Celsius ℃
    oled.show()

def configwifi(sid,pwd):
    global station,ap,ip,mask,gw,dns
    station.disconnect()
    station.connect(sid, pwd)
    for s in range(0, 50):     # i 0-49
        if not station.isconnected():
            time.sleep(0.1)
        else:
            ip = station.ifconfig()[0]
            mask = station.ifconfig()[1]
            gw = station.ifconfig()[2]
            dns = station.ifconfig()[3]
            print("Connection successful")
            # print(station.ifconfig())
            return True

    station.disconnect()
    print("out of 5s connect fail......")
    return False

def webserver():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(1)
    print("listen on 80.")
    while True:
        try:
            client, address = s.accept()
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
                # ssid=obj.group(1);pwd=obj.group(2)
                client.sendall("<p>Waiting......</p>")
                if configwifi(obj.group(1), obj.group(2)):
                    client.sendall("<p>Connect to {0} </p>".format(obj.group(1)))
                else:
                    client.sendall("<p>Fail......</p>")
            elif route[1]=='/api':
                client.sendall(json.dumps(Air))
            else:
                client.sendall("<h1>404 NOFOUND   ):</h1><hr><a href=\"https://github.com/hhh123123123\" style=\"text-decoration:none;\">Welcome to->MY GITHUB</a>")
            client.close()
        except:
            pass

def analysis():
    uart = UART(2, baudrate=115200, bits=8, rx=16, tx=17, stop=1, timeout=10)
    while True:
        time.sleep(1)
        if(uart.any()):
            rec=uart.read().decode()
            # print(rec)



if __name__ == '__main__':
    tim0 = Timer(0)
    tim1 = Timer(1)
    tim0.init(period=10000, mode=Timer.PERIODIC, callback=checkwifi)  # 检测WiFi是否断线,防止无限重连
    tim1.init(period=1000, mode=Timer.PERIODIC, callback=refresh_oled)  # 一秒刷新一次oled

    with open('wificonfig.json', "r") as f:
        jsondoc=json.loads(f.read())
    station.active(True)
    ssids = station.scan()
    for i in jsondoc['Sid_Pwd']:
        for j in ssids:
            if j[0].decode()==i['ssid']:
                if configwifi(i['ssid'],i['password']):
                    break

    ap.active(True)
    ap.config(essid="ESP32-Webconfig", authmode=4, password="12345678") #authmode=network.AUTH_WPA_WPA2_PSK=4

    # with open('wificonfig.json', "w") as f:
    #     f.write(json.dumps(jsondoc))
    # f = open('wificonfig.json', 'w')

    lock = _thread.allocate_lock()

    _thread.start_new_thread(webserver, ()) # 多线程运行webserver
    _thread.start_new_thread(analysis, ()) # 接受串口数据