from machine import Pin, I2C,Timer,UART
from micropython import mem_info
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
        print("client connected from", address, client)
        request = client.recv(1024)
        client.sendall('<script>alert("Configuration successful! This hotspot will be closed!");</script>')
        client.close()


if __name__ == '__main__':
    tim1.init(period=1000, mode=Timer.PERIODIC, callback=lambda t1: refresh_oled())  # 一秒刷新一次oled
    configwifi()
    ap.active(True)
    ap.config(essid="ESP32-Webconfig", authmode=network.AUTH_WPA_WPA2_PSK, password="12345678")
    # ssids=station.scan()
    # print(ssids)
    _thread.start_new_thread(webserver, ()) # 多线程运行webserver
    # _thread.start_new_thread(recstc8, ())

    while True:
        if(uart.any()):
            rec=uart.read().decode()
            # print(rec)