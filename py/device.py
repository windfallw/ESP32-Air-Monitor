from py import ssd1306, Webclient
import machine
import network
import binascii
import json
import time
import dht
import esp32
import gc

config = {
    'wifi': {'station': [{'ssid': 'example', 'password': 'yourpassword'}],
             'ap': {'essid': 'ESP32-Webconfig', 'password': '12345678', 'authmode': 4}},
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


def getSystemInfo(NetworkInfo, uart):
    CPU_freq = machine.freq()  # frequency must be 20MHz, 40MHz, 80Mhz, 160MHz or 240MHz
    CPU_temper = (esp32.raw_temperature() - 32) / 1.8
    # TSENS 值是一个字节，范围是 0 - 255，其数值变化和环境温度变化近似成线性关系，用户需要自己定义和测量其对应的外界温度值。
    hall = esp32.hall_sensor()  # 霍尔传感器的原始值
    allocRAM = gc.mem_alloc()
    freeRAM = gc.mem_free()
    systemInfo = {
        'networkinfo': NetworkInfo,
        'config': config,
        'sys': {'freq': CPU_freq, 'temper': CPU_temper, 'hall': hall, 'alloc': allocRAM, 'free': freeRAM},
        'log': {'OK200': [request.requestCount, request.requestSuccess], 'uart': uart}
    }
    return json.dumps(systemInfo)


# STAT_IDLE -- 没有连接，没有活动-1000
# STAT_CONNECTING -- 正在连接-1001
# STAT_WRONG_PASSWORD -- 由于密码错误而失败-202
# STAT_NO_AP_FOUND -- 失败，因为没有接入点回复,201
# STAT_GOT_IP -- 连接成功-1010
# STAT_ASSOC_FAIL -- 203
# STAT_BEACON_TIMEOUT -- 超时-200
# STAT_HANDSHAKE_TIMEOUT -- 握手超时-204

# wdt = machine.WDT(timeout=30000)#看门dog
# wdt.feed()

class WiFi:
    ip = "0.0.0.0"
    mask = "0.0.0.0"
    gateway = "0.0.0.0"
    dns = "0.0.0.0"
    RefreshWiFiStatus = False
    RefreshWiFiList = False
    wifi = config['wifi']['station']  # config里的WiFi设置
    station = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    NetworkInfo = {
        'station': {'network': (ip, mask, gateway, dns), 'essid': '', 'rssi': 0, 'status': 0, 'mac': '',
                    'isconnect': False},
        'ap': {'network': (), 'mac': '', 'essid': '', 'authmode': None},
        'scan': []
    }

    def __init__(self):
        self.station.active(True)
        self.loadExistWiFi()  # 在加载类的时候顺便自动连接已知的WIFI
        self.ap.active(True)
        self.ap.config(essid="ESP32-Webconfig", authmode=4,
                       password="12345678")  # authmode=network.AUTH_WPA_WPA2_PSK=4 channel最好选择1 6 11

    def interruptWiFi(self):
        if not self.RefreshWiFiStatus:
            self.RefreshWiFiStatus = True

    def WiFiStatus(self):
        self.NetworkInfo['station']['network'] = self.station.ifconfig()
        self.ip, self.mask, self.gateway, self.dns = self.NetworkInfo['station']['network']
        self.NetworkInfo['station']['status'] = self.station.status()
        if self.station.isconnected():
            self.NetworkInfo['station']['isconnect'] = True
            self.NetworkInfo['station']['essid'] = self.station.config('essid')
            self.NetworkInfo['station']['rssi'] = self.station.status('rssi')
        else:
            self.NetworkInfo['station']['isconnect'] = False
            self.NetworkInfo['station']['essid'] = ''
            self.NetworkInfo['station']['rssi'] = 0
        self.NetworkInfo['station']['mac'] = binascii.hexlify(self.station.config('mac'), ':').decode()
        self.NetworkInfo['ap']['network'] = self.ap.ifconfig()
        self.NetworkInfo['ap']['essid'] = self.ap.config('essid')
        self.NetworkInfo['ap']['authmode'] = self.ap.config('authmode')
        self.NetworkInfo['ap']['mac'] = binascii.hexlify(self.ap.config('mac'), ':').decode()

    def ScanWiFi(self):
        aps = self.station.scan()
        scan = []
        for ap in aps:
            ssid = ap[0].decode()
            mac = binascii.hexlify(ap[1], ':').decode()
            scan.append([ssid, mac, ap[2], ap[3], ap[4], ap[5]])  # [ssid，bssid，channel，RSSI，authmode，hidden]
        self.NetworkInfo['scan'] = scan
        return scan

    def ConnectWiFi(self, sid, pwd):
        self.station.disconnect()
        try:
            self.station.connect(sid, pwd)
            for s in range(0, 50):  # i 0-49
                if not self.station.isconnected():
                    time.sleep(0.1)
                else:
                    self.SaveWiFi(sid, pwd)
                    print("Connection successful")
                    return True
        except Exception as e:
            self.station.disconnect()
            print('WiFi:', e)
            return False
        finally:
            self.WiFiStatus()
        self.station.disconnect()
        print("out of 5s connect fail......")
        return False

    def loadExistWiFi(self):
        ssids = self.ScanWiFi()
        for i in self.wifi:
            for j in ssids:
                if j[0] == i['ssid']:
                    if self.ConnectWiFi(i['ssid'], i['password']):
                        return

    def SaveWiFi(self, sid, pwd):
        for i in self.wifi:
            if sid == i['ssid']:
                i['password'] = pwd
                write_config()
                return
        self.wifi.append({'ssid': sid, 'password': pwd})
        config['wifi']['station'] = self.wifi
        write_config()


class External:
    humidity = 0
    temperature = 0
    uartCount = 0
    uartSuccess = 0
    RefreshDHT = False
    RefreshOLED = False
    PMS7003 = '{"Gt0_3um":0,"Gt0_5um":0,"Gt10um":0,"Gt1_0um":0,"Gt2_5um":0,"Gt5_0um":0,"PM10AE":0,"PM10CF1":0,"PM1_0AE":0,"PM1_0CF1":0,"PM2_5AE":0,"PM2_5CF1":0,"humidity":0,"temperature":0,"type":"pms7003"}'
    GPS = '{"day":0,"hour":0,"lae1":0,"lae2":0,"loe1":0,"loe2":0,"minute":0,"month":0,"sec":0,"type":"gps","year":2020}'
    VOC = '{"CH2O":0,"CO2":0,"VOC":0,"type":"voc"}'

    def __init__(self):
        self.i2c = machine.I2C(scl=machine.Pin(15), sda=machine.Pin(4), freq=100000)
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)
        self.dht11 = dht.DHT11(machine.Pin(25))
        self.uart2 = machine.UART(2, baudrate=115200, bits=8, rx=16, tx=17, stop=1, timeout=10)

    def interruptDHT(self):
        if not self.RefreshDHT:
            self.RefreshDHT = True

    def interruptOLED(self):
        if not self.RefreshOLED:
            self.RefreshOLED = True

    def Screen(self, networkinfo):
        ip, mask, gateway, dns = networkinfo
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
            print('OLED:', e)

    def DHT(self):
        try:
            self.dht11.measure()
            self.humidity = self.dht11.humidity()
            self.temperature = self.dht11.temperature()
        except OSError:
            pass
        except Exception as e:
            print('DHT11:', e)

    def UART2(self):
        while True:
            try:
                if self.uart2.any():
                    self.uartCount += 1
                    UartRecv = self.uart2.readline().decode()
                    data = json.loads(UartRecv)
                    if data['type'] == 'pms7003':
                        data['humidity'] = self.humidity
                        data['temperature'] = self.temperature
                        self.PMS7003 = json.dumps(data)
                        request.send_json(self.PMS7003, config['client']['path'][data['type']])
                    elif data['type'] == 'gps':
                        self.GPS = json.dumps(data)
                        # STC8串口发送的json字符串带有\r\n这里也可以写成UartRecv.replace('\r\n', ''),务必去除\r\n否则js识别不出json格式
                        # request.send_json(self.GPS, config['client']['path'][data['type']])
                    elif data['type'] == 'voc':
                        self.VOC = json.dumps(data)
                        request.send_json(self.VOC, config['client']['path'][data['type']])
                    else:
                        raise Exception("无法识别的类型")
                    self.uartSuccess += 1
                else:
                    time.sleep_ms(50)  # 不加延迟且串口没有收到数据的时候会卡死
            except ValueError:
                pass
            except Exception as e:
                print('UART2:', e)
