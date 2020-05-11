# ESP32 Air Monitor
- 这是一个使用*MicroPython*开发的ESP32项目

- ESP32通过串口接收来自STC8的空气质量数据, 并提供网页服务来供使用者监控当前空气质量

- 有关*STC8*如何采集空气质量的请查看此[项目]((https://github.com/windfallw/STC8-Airsensor) )

## System Desigin

- 总共运行了三个线程

**第一个线程是WebServer线程提供了Web服务**

 1. 从Socket模块的监听到HTTP请求的解析以及HTTP响应头的构造以及Web服务路由表的建立都是自己实现的；
 2. 只需在`WebServant`类初始化时指定`static_path`和`template_path`即可在ESP32开机时自动加载相应的文件夹中的HTML CSS JavaScript 文件到路由表；
 
 *Example Usage of WebServer.py*
 
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
 
 
 


