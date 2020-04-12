from machine import Pin
import json
import dht

humidity = 0
temperature = 0
dht11 = dht.DHT11(Pin(25))

Requesterdir = {'Proto': 'http', 'host': 'www.example.com', 'Port': 80, 'method': 'POST',
                'Path': {'pms7003': '/info/sendair', 'gps': '/info/sendgps'}}
conf = {
    'Sid_Pwd': [{'ssid': 'example', 'password': 'yourpassword'}],
    'Requester': Requesterdir
}

PMS7003 = ''
GPS = ''


def rwjson(c):
    global conf
    try:
        if c:
            with open('config.json', "r") as f:
                conf = json.loads(f.read())
            f.close()
        else:
            with open('config.json', "w") as f:
                f.write(json.dumps(conf))
            f.close()
    except Exception:
        pass


def savewifi(sid, pwd):
    global conf
    for i in conf['Sid_Pwd']:
        if sid == i['ssid']:
            i['password'] = pwd
            rwjson(False)  # 写入json
            return
    conf['Sid_Pwd'].append({'ssid': sid, 'password': pwd})
    rwjson(False)


def saverequester(host, port):
    global conf
    Requesterdir['host'] = host
    Requesterdir['Port'] = port
    conf['Requester'] = Requesterdir
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
