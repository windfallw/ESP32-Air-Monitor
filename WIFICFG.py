"""
quick start:
=========================
import gc
from WIFICFG import WiFi

wifi = WiFi()
wifi.auto_run() #or wifi.auto_run("your_ssid", "your_password")
del wifi
gc.collect()
=========================
configuration mode:
connect to hotspot:ESP-WIFICFG(password:3.1415926)
access to (192.168.4.1) to configure wifi
"""

import os
import network
import time
import json
import usocket as socket
import ure as re



class WiFi:
    LOG = True

    def __init__(self, file="WIFICFG.json"):
        self.file = file
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(False)
        self.sta = network.WLAN(network.STA_IF)
        try:
            self.sta.disconnect()
        except OSError as e:
            pass
        self.sta.active(True)

    def auto_run(self, ssid=None, passwd=None, retry=0):
        ssids = self.scan()
        time.sleep(0.5)
        for i in range(retry+1):
            if ssid in ssids:
                if self.connect(ssid, passwd):
                    self.log("All done! Exiting wifi configuration!")
                    return
            else:
                if i != 0:
                    ssids = self.scan()
                    time.sleep(0.5)
        # try cfg_data to connect
        for i in range(retry+1):
            cfg_data = self.load_cfg()
            for each in ssids:
                if each in cfg_data.keys() and self.connect(each, cfg_data[each]):
                    self.log("All done! Exiting wifi configuration!")
                    return
            if i != 0:
                ssids = self.scan()
                time.sleep(0.5)
        self.on_connect_error()
        self.get_cfg_from_web()
        self.log("All done! Exiting wifi configuration!")

    def connect(self, ssid, passwd):
        self.sta.active(True)
        self.sta.disconnect()
        self.sta.connect(ssid, "" if passwd is None else passwd)
        self.log('Try connecting to ssid: %s' % ssid)
        for i in range(50):
            if not self.sta.isconnected():
                time.sleep(0.1)
            else:
                self.update_cfg(ssid, passwd)
                self.log('Connected to ssid: %s' % ssid)
                return True
        self.sta.disconnect()
        self.log('Failed to connect to ssid: %s' % ssid)
        return False

    def load_cfg(self):
        if self.file in os.listdir():
            with open(self.file, "r") as f:
                return json.loads(f.read())
        return {}

    def update_cfg(self, ssid, passwd):
        data = self.load_cfg()
        data[ssid] = passwd
        with open(self.file, "w") as f:
            f.write(json.dumps(data))

    def scan(self):
        # should set self.sta.active(True) before self.scan()
        ssids = self.sta.scan()
        _ssids = [(i[0], i[3]) for i in ssids]
        _ssids.sort(key=lambda x:x[1], reverse=True)
        return [i[0].decode('utf-8') for i in _ssids]

    def log(self, *args, **kws):
        if self.LOG:
            for each in args[0:-1]:
                print(each, end=" ")
            print(args[-1])
            if "end" in kws.keys():
                print(kws["end"])
            else:
                print("\n")

    def get_cfg_from_web(self):
        ssids = self.scan()
        time.sleep(0.5)
        self.ap.active(True)
        html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no"/><title>WIFI-CFG</title><style>*{margin:0;padding:0;box-sizing:border-box;}body{font-family: "微软雅黑",sans-serif;}.login {position: absolute;top: 50%%;left: 50%%;margin: -150px 0 0 -150px;width:300px;height:300px;}.login h1 { color:#555555; text-shadow: 0px 10px 8px #CDC673; letter-spacing:2px;text-align:center;margin-bottom:20px; }input, select{padding:10px;width:100%%;color:white;margin-bottom:10px;background-color:#555555;border: 1px solid black;border-radius:4px;letter-spacing:2px;}form button{width:100%%;padding:10px;margin: 5px 0 0 0;background-color:#87CEFA;border:1px solid black;border-radius:4px;cursor:pointer;}</style></head><script>window.alert = function(name){var iframe = document.createElement("IFRAME");iframe.style.display="none";iframe.setAttribute("src", 'data:text/plain,');document.documentElement.appendChild(iframe);window.frames[0].window.alert(name);iframe.parentNode.removeChild(iframe);}</script>%s<body><div class="headtop"></div><div class="login"><h1>WIFI-CFG</h1><form action="" method="get"><select name="SSID">%s</select><input type="password" name="PASSWORD" placeholder="Password" required="required"><button type="submit">Submit</button></form></div></body></html>"""
        self.ap.config(essid="ESP-WIFICFG", authmode=network.AUTH_WPA_WPA2_PSK, password="3.1415926")
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind(('0.0.0.0', 80))
        skt.listen(1)
        self.log('listen on', ('192.168.4.1', 80))
        ok = False
        while True:
            try:
                _html = ""
                for each in ssids:
                    _html += ('<option value ="%s">%s</option>' % (each, each))
                client, address = skt.accept()
                self.log("client connected from", address, client)
                request = client.recv(1024)
                error = False
                line1 = request.decode('utf-8').split('\n')[0]
                form = re.compile(r'[?]SSID=(.+)&PASSWORD=(.+) HTTP/1').search(line1)
                if form:
                    ssid = form.group(1)
                    passwd = form.group(2)
                    if self.connect(ssid, passwd):
                        ok = True
                    else:
                        error = True
                if ok:
                    client.sendall(html % ("""<script>alert("Configuration successful! This hotspot will be closed!");</script>""", _html))
                    client.close()
                    self.ap.active(False)
                    time.sleep(5)
                    break
                else:
                    client.sendall(html % ("""<script>alert("Wrong password! Please re-input!");setTimeout('window.location.href="http://192.168.4.1"', 0.1);</script>""" if error else '', _html))
                    if line1.split(" ")[1] == "/":
                        ssids = self.scan()
                        time.sleep(0.5)
                client.close()
            except OSError as e:
                self.log(e)

    def on_connect_error(self):
        pass

