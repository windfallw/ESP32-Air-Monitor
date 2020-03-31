from machine import Pin
import json
import dht

humidity = 0
temperature = 0
dht11 = dht.DHT11(Pin(25))

jsondoc = {
    'Sid_Pwd': [{'ssid': 'example', 'password': 'yourpassword'}]
}

Air = {"PM2_5AE": "0", "Gt0_5um": "0", "humidity": 0, "PM1_0AE": "0", "PM2_5CF1": "0", "temperature": 0,
       "Gt0_3um": "0", "PM1_0CF1": "0", "Gt1_0um": "0", "Gt2_5um": "0", "Gt5_0um": "0", "PM10AE": "0",
       "type": "pms7003", "PM10CF1": "0", "Gt10um": "0"}

GPS = {"type": "gps", "day": "0", "year": "0", "loe1": "0", "lae1": "0", "month": "0", "loe2": "0", "lae2": "0"}

String_Air = json.dumps(Air)
String_GPS = json.dumps(GPS)


def rwjson(c):
    global jsondoc
    try:
        if c:
            with open('wificonfig.json', "r") as f:
                jsondoc = json.loads(f.read())
            f.close()
        else:
            with open('wificonfig.json', "w") as f:
                f.write(json.dumps(jsondoc))
            f.close()
    except:
        pass


def savekey(sid, pwd):
    global jsondoc
    for i in jsondoc['Sid_Pwd']:
        if sid == i['ssid']:
            i['password'] = pwd
            rwjson(False)  # 写入json
            return
    jsondoc['Sid_Pwd'].append({'ssid': sid, 'password': pwd})
    rwjson(False)


def releasepack(data):
    global Air, GPS, String_Air, String_GPS
    try:
        jsLoads = json.loads(data)
        if jsLoads['type'] == 'pms7003':
            Air = jsLoads
            Air['humidity'] = humidity
            Air['temperature'] = temperature
            String_Air = json.dumps(Air)
        elif jsLoads['type'] == 'gps':
            GPS = jsLoads
            String_GPS = json.dumps(GPS)
    except ValueError as e:
        print(e)
        print(data)


def releasedht():
    global humidity, temperature
    try:
        dht11.measure()
        humidity = dht11.humidity()
        temperature = dht11.temperature()
    except OSError:
        print("OSError in dht")
    return humidity, temperature
