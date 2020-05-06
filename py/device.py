from py import ssd1306, Webclient
import machine
import network
import json
import time
import dht

config = {
    'wifi': [{'ssid': 'example', 'password': 'yourpassword'}],
    'client': {'proto': 'http', 'host': 'www.example.com', 'port': 80, 'method': 'POST',
               'path': {'pms7003': '/info/sendair', 'gps': '/info/sendgps', 'voc': '/info/sendvoc'}}
}


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


def save_client(host, port):
    client = config['client']
    client['host'] = host
    client['port'] = port
    config['client'] = client
    write_config()


read_config()
request = Webclient.HttpRequest(config['client'])


# wdt = machine.WDT(timeout=30000)#看门dog
# machine.reset()重启
# wdt.feed()

class WiFi:
    ip = "0.0.0.0"
    mask = "0.0.0.0"
    gateway = "0.0.0.0"
    dns = "0.0.0.0"
    network_config = (ip, mask, gateway, dns)
    wifi = []
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)

    def __init__(self):
        self.load_wifi()
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
                    self.save_wifi(sid, pwd)
                    print("Connection successful")
                    return True
        finally:
            self.network_config = self.station.ifconfig()
            self.ip, self.mask, self.gateway, self.dns = self.station.ifconfig()
        self.station.disconnect()
        print("out of 5s connect fail......")
        return False

    def load_wifi(self):
        self.wifi = config['wifi']
        self.station.active(True)
        ssids = self.station.scan()
        for i in self.wifi:
            for j in ssids:
                if j[0].decode() == i['ssid']:
                    if self.connect_wifi(i['ssid'], i['password']):
                        return

    def save_wifi(self, sid, pwd):
        for i in self.wifi:
            if sid == i['ssid']:
                i['password'] = pwd
                write_config()
                return
        self.wifi.append({'ssid': sid, 'password': pwd})
        config['wifi'] = self.wifi
        write_config()


class External:
    humidity = 0
    temperature = 0
    PMS7003 = '{"Gt0_3um":0,"Gt0_5um":0,"Gt10um":0,"Gt1_0um":0,"Gt2_5um":0,"Gt5_0um":0,"PM10AE":0,"PM10CF1":0,"PM1_0AE":0,"PM1_0CF1":0,"PM2_5AE":0,"PM2_5CF1":0,"humidity":0,"temperature":0,"type":"pms7003"}'
    GPS = '{"day":0,"hour":0,"lae1":0,"lae2":0,"loe1":0,"loe2":0,"minute":0,"month":0,"sec":0,"type":"gps","year":2020}'
    VOC = '{"CH2O":0,"CO2":0,"VOC":0,"type":"voc"}'

    def __init__(self):
        self.i2c = machine.I2C(scl=machine.Pin(15), sda=machine.Pin(4), freq=100000)
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)
        self.dht11 = dht.DHT11(machine.Pin(25))
        self.uart2 = machine.UART(2, baudrate=115200, bits=8, rx=16, tx=17, stop=1, timeout=10)

    def Screen(self, network_config):
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

    def DHT(self):
        try:
            self.dht11.measure()
            self.humidity = self.dht11.humidity()
            self.temperature = self.dht11.temperature()
        except Exception as e:
            print('DHT11:', e)

    def UART2(self):
        while True:
            try:
                if self.uart2.any():
                    UartRecv = self.uart2.readline().decode()
                    data = json.loads(UartRecv)
                    if data['type'] == 'pms7003':
                        data['humidity'] = self.humidity
                        data['temperature'] = self.temperature
                        self.PMS7003 = json.dumps(data)
                        request.send_json(self.PMS7003, config['client']['path'][data['type']])
                    elif data['type'] == 'gps':
                        self.GPS = json.dumps(data)
                        # request.send_json(self.GPS, config['client']['path'][data['type']])
                    elif data['type'] == 'voc':
                        self.VOC = json.dumps(data)
                        request.send_json(self.VOC, config['client']['path'][data['type']])
                    else:
                        raise Exception("无法识别的类型")
            except ValueError:
                pass
            except Exception as e:
                print('UART2:', e)
            time.sleep_ms(50)  # 不加延迟且串口没有收到数据的时候会卡死
