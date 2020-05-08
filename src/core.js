let authmode = {
    AUTH_OPEN: 0,
    AUTH_WEP: 1,
    AUTH_WPA_PSK: 2,
    AUTH_WPA2_PSK: 3,
    AUTH_WPA_WPA2_PSK: 4,
    AUTH_MAX: 6
};

function getSys() {
    $.ajax({
        type: "get",
        url: "sysinfo",
        data: {},
        dataType: 'json',
        async: true, //是否为异步请求，ture为异步请求，false为同步请求
        timeout: 1000,
        beforeSend: LoadFunction, //加载执行方法
        error: erryFunction, //错误执行方法
        success: succFunction //成功执行方法
    });

    function LoadFunction() {
    }

    function erryFunction() {
    }

    function succFunction(d) {
        let freeRam = d.sys.free;
        let allocRam = d.sys.alloc;
        let freq = d.sys.freq;
        let temper = Math.trunc((d.sys.temper - 32) / 1.8);//TSENS 值是一个字节，范围是 0 - 255，其数值变化和环境温度变化近似成线性关系，用户需要自己定义和测量其对应的外界温度值。
        let hall = d.sys.hall;
        let networkInfo = d.networkinfo;
        let log = d.log;
        let config = d.config;
        showWiFiStatus(networkInfo.station);
        showStationInfo(networkInfo.station);
        showApInfo(networkInfo.ap);
        showCpuFreq(freq);
        showRAM([freeRam, allocRam]);
        showUartHttpCount(log);
    }
}

function machineReset() {
    $.ajax({
        type: "post",
        url: "reset",
        data: 'reset',
        dataType: 'text',
        async: true, //是否为异步请求，ture为异步请求，false为同步请求
        timeout: 1000,
        beforeSend: LoadFunction, //加载执行方法
        error: erryFunction, //错误执行方法
        success: succFunction //成功执行方法
    });

    function LoadFunction() {
    }

    function erryFunction() {
        console.log('服务器未响应');
    }

    function succFunction(d) {
        if (d === 'reset') console.log('服务器已响应重启命令');
    }
}

function showApInfo(ap) {
    let ssid = ap.essid;
    let mac = ap.mac;
    let mode = ap.authmode;
    let network = ap.network;
    let str = '';
    str += '<p class="text-gray-900">AP热点名称: ' + ssid + '</p>';
    for (let key in authmode) {
        if (authmode[key] === mode) {
            str += '<p class="text-gray-900">认证模式: ' + key + '</p>';
            break;
        }
    }
    str += '<p class="text-gray-900">IP: ' + network[0] + '</p>';
    str += '<p class="text-gray-900">子网掩码: ' + network[1] + '</p>';
    str += '<p class="text-gray-900">网关: ' + network[2] + '</p>';
    str += '<p class="text-gray-900">DNS服务器: ' + network[3] + '</p>';
    str += '<p class="text-gray-900">Access Point MAC地址: ' + mac + '</p>';
    $('#apInfo').html(str);
}


function showStationInfo(station) {
    let mac = station.mac;
    let network = station.network;
    let str = '';
    str += '<p class="text-gray-900">IP: ' + network[0] + '</p>';
    str += '<p class="text-gray-900">子网掩码: ' + network[1] + '</p>';
    str += '<p class="text-gray-900">网关: ' + network[2] + '</p>';
    str += '<p class="text-gray-900">DNS服务器: ' + network[3] + '</p>';
    str += '<p class="text-gray-900">Station MAC地址: ' + mac + '</p>';
    $('#stationInfo').html(str);
}

function showWiFiStatus(networkInfo) {
    let isconnect = networkInfo.isconnect;
    let status = networkInfo.status;
    let rssi = networkInfo.rssi;
    let essid = networkInfo.essid;
    let span = $('#essid');
    let icon = $('#wifiIcon');
    if (isconnect) {
        span.text(essid + ' (' + rssi + 'dBm)');
        if (rssi > -50) icon.attr("class", "iconfont icon-wifi-4 text-gray-600");
        else if (rssi > -60) icon.attr("class", "iconfont icon-wifi-3 text-gray-600");
        else if (rssi > -70) icon.attr("class", "iconfont icon-wifi-2 text-gray-600");
        else icon.attr("class", "iconfont icon-wifi-1");
    } else if (status === 1001) {
        span.text('WiFi连接中...');
        icon.attr("class", "iconfont icon-wifi-disabled text-gray-600");
    } else {
        span.text('WiFi连接中断');
        icon.attr("class", "iconfont icon-wifi-disabled text-gray-600");
    }
}

function showCpuFreq(freq) {
    // frequency must be 20MHz, 40MHz, 80Mhz, 160MHz or 240MHz
    freq = freq / 1000000;//转换为MHZ
    $('#freq').text(freq + 'MHZ');
}

function showRAM(ram) {
    let ramSpace = ram[0] + ram[1];
    let ramPercent = Math.trunc(ram[1] / ramSpace * 100);
    $('#ramText').text("内存使用情况 (" + ram[1] + "/" + ram[0] + ")");
    $('#ramPercent').text(ramPercent + "%");
    $('#ramProgress').css("width", ramPercent + "%").attr('aria-valuenow', ramPercent);
}

function showUartHttpCount(log) {
    let uart = log.uart;
    let http = log.OK200;
    $('#uartCount').text(uart[1] + '/' + uart[0]);
    $('#httpCount').text(http[1] + '/' + http[0]);
}


getSys();
setInterval(getSys, 5000)