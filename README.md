# ESP32 Air Monitor
- 这是一个使用*MicroPython*开发的ESP32项目

- ESP32通过串口接收来自STC8的空气质量数据, 并提供网页服务来供使用者监控当前空气质量

![devices](images/devices.jpg)

- 有关*STC8*如何采集空气质量的请查看此[项目](https://github.com/windfallw/STC8-Airsensor)

## System Design

 总共运行了三个线程

**1. 第一个线程是WebServer线程提供了Web服务**

 - 从Socket模块的监听到HTTP请求的解析以及HTTP响应头的构造以及Web服务路由表的建立都是自己实现的；
 - 只需在`WebServant`类初始化时指定`static_path`和`template_path`即可在ESP32开机时自动加载相应的文件夹中的HTML CSS JavaScript 文件到路由表；

 ***Example Usage of WebServer.py***

 ```python
from py import Webserver
app = Webserver.WebServant(static_path='/src', template_path='/www')
#static_path只会加载JS CSS文件 template_path只会加载HTML文件 如不需要加载可放空
 ```

 *Redirect Example*
```text
flash/www/index.html ---> http://YourESP32IP/index.html
flash/src/sb-admin-2.min.css ---> http://YourESP32IP/src/sb-admin-2.min.css
```

 *Use Decorator to add more route*
```python
#Get方法的argument返回二个参数 client用于发送套接字 address是当前访问服务器的IP
@app.route('/','get')
def index(*arguments):
    client, address = arguments
    client.send(Webserver.header200())
    with open('www/index.html', 'rb') as f:
        line = f.read(8192)
        while line:
            client.send(line)
            line = f.read(8192)
        f.close()

#POST方法返回三个参数  client_data是客户发送的数据
@app.route('/machine', 'post')
def machineCtl(*arguments):
    client, address, client_data = arguments
    if client_data == 'reset':
        client.send(Webserver.header200('text'))
        client.send(client_data)
        client.close()
        machine.reset()
    else:
        client.send(Webserver.BadRequest400)
```

 *Attention*

 - 目前仅支持GET和POST方法的请求, 响应头仅实现了部分, 如有需求请自行添加；
 - 每次处理web请求后都会调用`gc.collect()`释放内存；

 ```python
print(app.route_table_get) # GET路由表
print(app.route_table_post) # POST路由表
_thread.start_new_thread(app.run, ('0.0.0.0', 80)) # 建议使用线程运行
 ```

- - -

**2. 第二个线程是串口接收数据并传送到服务器数据库保存**

- 读取STC8发送的的**JSON**格式数据解析后与DHT11采集的温湿度一同打包上传到服务器, 同时本地保留供Web服务调用；

- 因为该部分代码不具有可重用性所以不做过多的介绍;

- - -

**3. 第三个线程涉及到的功能较多确保了ESP32的稳定运行**

- 首先此线程涉及到三个定时器的运作

```python
    tim0 = machine.Timer(0)
    tim1 = machine.Timer(1)
    tim2 = machine.Timer(2)
    tim0.init(period=10000, mode=machine.Timer.PERIODIC,
              callback=lambda t: WiFi.interruptWiFi())  # 10秒读取一次WiFi状态,断线自动重连
    tim1.init(period=5000, mode=machine.Timer.PERIODIC,
              callback=lambda t: External_Device.interruptDHT())  # 5秒读取一次dht
    tim2.init(period=1000, mode=machine.Timer.PERIODIC,
              callback=lambda t: External_Device.interruptOLED())  # 1秒刷新一次OLED
```

 - 这些回调函数会将对应设备的中断标志设置为`True`，而此线程则负责扫描中断标志并执行相应的操作
  
   - DHT11的温湿度采集
   
   - OLED屏的刷新
   
   - WIFI状态的检测
   
     - 刷新WIFI状态获取相关参数供Web服务调用
     - 如果检测到WIFI中断则会自动连接已保存的WIFI
     - 响应服务器的`scan`扫描WIFI请求 (需要注意的是扫描WIFI时线程可能会受影响)
   
 ```python
def Refresh():
    while True:
        if External_Device.RefreshDHT:
            External_Device.RefreshDHT = False
            External_Device.DHT()
        if External_Device.RefreshOLED:
            External_Device.RefreshOLED = False
            External_Device.Screen(WiFi.NetworkInfo['station']['network'])
        if WiFi.RefreshWiFiStatus:
            WiFi.RefreshWiFiStatus = False
            WiFi.WiFiStatus()
            if WiFi.station.status() not in [1001, 1010]:
                print('WiFiStatus:', WiFi.station.status())
                WiFi.loadExistWiFi()
        if WiFi.RefreshWiFiList:
            WiFi.RefreshWiFiList = False
            WiFi.ScanWiFi()
        time.sleep_ms(50)  # 找点事做防止线程卡死循环
 ```

- WIFI配置及相关系统设置的保存暂时存储在`flash/config.json`下未来可能会尝试使用`btree`数据库实现

## Web Design

 - 使用到的相关技术
   
   - 基于*Bootstrap*的*SB-Admin-2*框架
   
   - 图表的绘制使用*Chart.js*
   
   - GPS地图使用了[*高德地图API*](https://lbs.amap.com/)
   
   - 网页图标使用的是阿里的 [*Icon Font*](https://www.iconfont.cn/)

------

- 交互界面

  - 显示ESP32的设备概况
    - CPU工作频率
    - 内存使用情况
    - 串口接收STC8数据的次数统计
    - 将数据传输到服务器的次数统计
    - CPU温度和霍尔传感器
  - WiFi模块
    - 当前连接的SSID以及信号显示
    - 查看Station和AP的相关配置信息
  - PMS7003
  - DHT11
  - GPS地图

![WEB UI](images/web1.png)

- 交互设置
  - 重启ESP32
  - 连接WiFi
  - 修改服务器域名
  - 表格显示了ESP32当前扫描到的周围WiFi
  - 记录每次后台Ajax的交互

![WEB CONFIG](images/web2.png)

------

- 网页组件

   - `www` ----------> `Flash/www/...`

     - `favicon.ico`
     
     - `index.html`
     
   - `src` ----------> `Flash/src/...`

   	 - 框架所需要的组件
        - `sb-admin-2.min.css`
        - `font.css`
        - `ubuntuMono.css`
        - `Chart.min.js`
        - `bootstrap.bundle.min.js`
        - `jquery.min.js`
        - `sb-admin-2.min.js`
        - `jquery.easing.min.js`
      
     - JavaScript
        - `core.js`
          - Web端与ESP32的交互以及大部分功能都在这里实现
        - `setchart.js`
          - 包括了表格初始化等各种函数
        - `setmap.js`
          - 包括了地图初始化等各种函数 

## 其它

  - `Safari`浏览器的机制与其它主流浏览有所区别,建议使用`Chrome`或`Firefox`访问Web端
  - `WebServer`目前仍处于测试阶段
  