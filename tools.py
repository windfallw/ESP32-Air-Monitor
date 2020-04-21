import machine
import network
import ssd1306
import json
import time
import dht

# wdt = machine.WDT(timeout=30000)#看门dog
# machine.reset()重启
# wdt.feed()
humidity = 0
temperature = 0
dht11 = dht.DHT11(machine.Pin(25))

httpRequest_config = {'Proto': 'http', 'host': 'www.example.com', 'Port': 80, 'method': 'POST',
                      'Path': {'pms7003': '/info/sendair', 'gps': '/info/sendgps', 'voc': '/info/sendvoc'}}
config = {
    'network': [{'ssid': 'example', 'password': 'yourpassword'}],
    'httpRequest_config': httpRequest_config
}

PMS7003 = ''
GPS = ''


class WiFi:
    ip = "0.0.0.0"
    mask = "0.0.0.0"
    gw = "0.0.0.0"
    dns = "0.0.0.0"
    network_config = (ip, mask, gw, dns)
    ap = network.WLAN(network.AP_IF)
    station = network.WLAN(network.STA_IF)
    tim0 = machine.Timer(0)

    def __init__(self):
        self.firstload()
        self.ap.active(True)
        self.ap.config(essid="ESP32-Webconfig", authmode=4, password="12345678")  # authmode=network.AUTH_WPA_WPA2_PSK=4

    def checkwifi(self):
        if not self.station.isconnected():
            self.station.disconnect()
        # if ap.isconnected()

    def configwifi(self, sid, pwd):
        self.station.disconnect()
        self.station.connect(sid, pwd)
        try:
            for s in range(0, 50):  # i 0-49
                if not self.station.isconnected():
                    time.sleep(0.1)
                else:
                    print("Connection successful")
                    self.savewifi(sid, pwd)
                    # print(station.ifconfig())
                    return True
        finally:
            self.network_config = self.station.ifconfig()
            self.ip, self.mask, self.gw, self.dns = self.station.ifconfig()
        self.station.disconnect()
        print("out of 5s connect fail......")
        return False

    def firstload(self):
        rwjson(True)  # 读取json文件里的数据
        self.station.active(True)
        ssids = self.station.scan()
        for i in config['network']:
            for j in ssids:
                if j[0].decode() == i['ssid']:
                    if self.configwifi(i['ssid'], i['password']):
                        return

    def savewifi(self, sid, pwd):
        global config
        for i in config['network']:
            if sid == i['ssid']:
                i['password'] = pwd
                rwjson(False)  # 写入json
                return
        config['network'].append({'ssid': sid, 'password': pwd})
        rwjson(False)


class Oled:
    i2c = machine.I2C(scl=machine.Pin(15), sda=machine.Pin(4), freq=100000)
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    tim1 = machine.Timer(1)

    def __init__(self):
        pass
        # self.tim1.init(period=3000, mode=machine.Timer.PERIODIC, callback=self.refresh_oled)  # 3秒刷新一次oled

    def refresh_oled(self, network_config):
        h, t = releasedht()
        ip, mask, gw, dns = network_config
        try:
            self.oled.fill(0)
            self.oled.text("I" + ip, 0, 0, 1)
            self.oled.text("G" + gw, 0, 9, 1)
            self.oled.text("Humidity:" + str(h) + "%", 0, 18, 1)
            self.oled.text("Temperature:" + str(t) + "'C", 0, 27, 1)  # Celsius ℃
            self.oled.show()
        except Exception as e:
            print('Oled:', e)


def rwjson(c):
    global config
    try:
        if c:
            with open('config.json', "r") as f:
                config = json.loads(f.read())
            f.close()
        else:
            with open('config.json', "w") as f:
                f.write(json.dumps(config))
            f.close()
    except Exception:
        pass


def savehttpRequest(host, port):
    global config
    httpRequest_config['host'] = host
    httpRequest_config['Port'] = port
    config['httpRequest_config'] = httpRequest_config
    rwjson(False)


def releasepack(data):
    global PMS7003, GPS
    js_loads = json.loads(data)
    if js_loads['type'] == 'pms7003':
        js_loads['humidity'] = humidity
        js_loads['temperature'] = temperature
        PMS7003 = json.dumps(js_loads)
    elif js_loads['type'] == 'gps':
        js_loads['lae2'] = 0
        js_loads['loe2'] = 0
        GPS = json.dumps(js_loads)
    return js_loads


def releasedht():
    global humidity, temperature
    try:
        dht11.measure()
        humidity = dht11.humidity()
        temperature = dht11.temperature()
    except Exception as e:
        print('DHT11:', e)
    return humidity, temperature
