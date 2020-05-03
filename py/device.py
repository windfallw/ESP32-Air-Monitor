from py import ssd1306
import machine
import network
import json
import time
import dht

# wdt = machine.WDT(timeout=30000)#看门dog
# machine.reset()重启
# wdt.feed()

config = {
    'wifi_config': [{'ssid': 'example', 'password': 'yourpassword'}],
    'client_config': {'Proto': 'http', 'host': 'www.example.com', 'Port': 80, 'method': 'POST',
                      'Path': {'pms7003': '/info/sendair', 'gps': '/info/sendgps', 'voc': '/info/sendvoc'}}
}

PMS7003 = ''
GPS = ''


class WiFi:
    ip = "0.0.0.0"
    mask = "0.0.0.0"
    gateway = "0.0.0.0"
    dns = "0.0.0.0"
    network_config = (ip, mask, gateway, dns)
    wifi_config = []
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    tim0 = machine.Timer(0)

    def __init__(self):
        self.load_wifi_config()
        self.ap.active(True)
        self.ap.config(essid="ESP32-Webconfig", authmode=4, password="12345678")  # authmode=network.AUTH_WPA_WPA2_PSK=4

    def check_wifi_disconnect(self):
        if not self.station.isconnected():
            self.station.disconnect()

    def connect_wifi(self, sid, pwd):
        self.station.connect(sid, pwd)
        try:
            for s in range(0, 50):  # i 0-49
                if not self.station.isconnected():
                    time.sleep(0.1)
                else:
                    self.save_wifi_config(sid, pwd)
                    print("Connection successful")
                    return True
        finally:
            self.network_config = self.station.ifconfig()
            self.ip, self.mask, self.gateway, self.dns = self.station.ifconfig()
        self.station.disconnect()
        print("out of 5s connect fail......")
        return False

    def load_wifi_config(self):
        read_config()
        self.wifi_config = config['wifi_config']
        self.station.active(True)
        ssids = self.station.scan()
        for i in self.wifi_config:
            for j in ssids:
                if j[0].decode() == i['ssid']:
                    if self.connect_wifi(i['ssid'], i['password']):
                        return

    def save_wifi_config(self, sid, pwd):
        for i in self.wifi_config:
            if sid == i['ssid']:
                i['password'] = pwd
                write_config()
                return
        self.wifi_config.append({'ssid': sid, 'password': pwd})
        config['wifi_config'] = self.wifi_config
        write_config()


class External:
    tim1 = machine.Timer(1)
    tim2 = machine.Timer(2)
    humidity = 0
    temperature = 0

    def __init__(self):
        self.dht11 = dht.DHT11(machine.Pin(25))
        self.i2c = machine.I2C(scl=machine.Pin(15), sda=machine.Pin(4), freq=100000)
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)

    def refresh_screen(self, network_config):
        ip, mask, gateway, dns = network_config
        try:
            self.oled.fill(0)
            self.oled.text("Temperature:%s'C" % self.temperature, 0, 0, 1)  # Celsius ℃
            self.oled.text("Humidity:{0}{1}".format(self.humidity, '%'), 0, 8, 1)
            self.oled.text("IP:", 0, 19, 1)
            self.oled.text(ip, 0, 30, 1)
            self.oled.text("Gateway:", 0, 41, 1)
            self.oled.text(gateway, 0, 52, 1)

            self.oled.show()
        except Exception as e:
            print('Oled:', e)

    def release_dht(self):
        try:
            self.dht11.measure()
            self.humidity = self.dht11.humidity()
            self.temperature = self.dht11.temperature()
        except Exception as e:
            print('DHT11:', e)

    def pack(self, data):
        global PMS7003, GPS
        js_loads = json.loads(data)
        if js_loads['type'] == 'pms7003':
            js_loads['humidity'] = self.humidity
            js_loads['temperature'] = self.temperature
            PMS7003 = json.dumps(js_loads)
        elif js_loads['type'] == 'gps':
            js_loads['lae2'] = 0
            js_loads['loe2'] = 0
            GPS = json.dumps(js_loads)
        return js_loads


def read_config():
    global config
    try:
        with open('config.json', "r") as f:
            config = json.loads(f.read())
        f.close()
    except Exception as e:
        print('read_config:', e)


def write_config():
    try:
        with open('config.json', "w") as f:
            f.write(json.dumps(config))
        f.close()
    except Exception as e:
        print('write_config:', e)


def save_client_config(host, port):
    client_config = config['client_config']
    client_config['host'] = host
    client_config['Port'] = port
    config['client_config'] = client_config
    write_config()
