let gpsData;
let markArry = [];
let autoGetGps;
let mapOption = {
    zoom: 15,
    mapStyle: 'amap://styles/blue',
    viewMode: '2D',
    lang: 'zh_cn',
    features: ['bg', 'road', 'building', 'point'],
};
let GdMap = new AMap.Map(document.getElementById("Map"), mapOption);
AMap.plugin([
    'AMap.ToolBar',
    'AMap.Scale',
    'AMap.OverView',
    'AMap.MapType',
    'AMap.Geolocation',
], function () {
    // 在图面添加工具条控件，工具条控件集成了缩放、平移、定位等功能按钮在内的组合控件
    // GdMap.addControl(new AMap.ToolBar());
    // 在图面添加比例尺控件，展示地图在当前层级和纬度下的比例尺
    GdMap.addControl(new AMap.Scale());
    // 在图面添加鹰眼控件，在地图右下角显示地图的缩略图
    //GdMap.addControl(new AMap.OverView({isOpen:true}));
    // 在图面添加类别切换控件，实现默认图层与卫星图、实施交通图层之间切换的控制
    //GdMap.addControl(new AMap.MapType());
    // 在图面添加定位控件，用来获取和展示用户主机所在的经纬度位置
    //    GdMap.addControl(new AMap.Geolocation());
});

function convert(gps) {
    let convertlaeloe;
    let mark = new AMap.Marker();
    AMap.convertFrom(gps, 'gps', function (status, result) {
        if (result.info === 'ok') {
            convertlaeloe = result.locations[0];
            mark = new AMap.Marker({
                position: convertlaeloe,
            });
            GdMap.add(mark);
            GdMap.setFitView();
            markArry.push(mark);
        }
    });
}

function getGps() {
    $.ajax({
        type: "get",
        url: serverAddress + "info/gps",
        data: {},
        dataType: 'json',
        async: true, //是否为异步请求，ture为异步请求，false为同步请求
        timeout: 5000,
        beforeSend: LoadFunction, //加载执行方法
        error: erryFunction, //错误执行方法
        success: succFunction //成功执行方法
    });

    function LoadFunction() {
    }

    function erryFunction() {
        serverResponse(this.url + ' -> Fail', true);
    }

    function succFunction(d) {
        serverResponse(this.url + ' -> Success');
        if (gpsData === JSON.stringify(d)) return;
        let time;
        let lae, loe;
        let day, month, year, hour, minute, sec;
        gpsData = JSON.stringify(d);
        day = d.day;
        month = d.month;
        year = d.year;
        hour = d.hour;
        minute = d.minute;
        sec = d.sec
        lae = d.lae1 + d.lae2 / 60; //纬度
        loe = d.loe1 + d.loe2 / 60; //经度
        time = year + '-' + month + '-' + day + ' ' + hour + ':' + minute + ':' + sec;
        convert([loe, lae]);
    }
}

function closeAutoGetGps() {
    clearInterval(autoGetGps);
}
