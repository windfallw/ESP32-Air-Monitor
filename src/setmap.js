let gpsData;
let markArry = [];
let mapOption = {
    zoom: 15,
    mapStyle: 'amap://styles/blue',
    viewMode: '2D',
    lang: 'zh_cn',
    features: ['bg', 'road', 'building', 'point'],
};
let map1 = new AMap.Map(document.getElementById("MAP"), mapOption);
AMap.plugin([
    'AMap.ToolBar',
    'AMap.Scale',
    'AMap.OverView',
    'AMap.MapType',
    'AMap.Geolocation',
], function () {
    // 在图面添加工具条控件，工具条控件集成了缩放、平移、定位等功能按钮在内的组合控件
    // map1.addControl(new AMap.ToolBar());
    // 在图面添加比例尺控件，展示地图在当前层级和纬度下的比例尺
    map1.addControl(new AMap.Scale());
    // 在图面添加鹰眼控件，在地图右下角显示地图的缩略图
    //map1.addControl(new AMap.OverView({isOpen:true}));
    // 在图面添加类别切换控件，实现默认图层与卫星图、实施交通图层之间切换的控制
    //map1.addControl(new AMap.MapType());
    // 在图面添加定位控件，用来获取和展示用户主机所在的经纬度位置
    //    map1.addControl(new AMap.Geolocation());
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
            map1.add(mark);
            map1.setFitView();
            markArry.push(mark);
        }
    });
}

function getGps() {
    let lae, loe;
    let lae1, lae2, loe1, loe2, day, month, year;
    let laeloe = [0, 0];
    $.ajax({
        type: "get",
        url: "/info/gps",
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
        if (gpsData === JSON.stringify(d)) {
            return;
        }
        gpsData = JSON.stringify(d);
        day = d.day;
        month = d.month;
        year = d.year;
        lae1 = parseInt(d.lae1);
        lae2 = parseFloat(d.lae2);
        loe1 = parseInt(d.loe1);
        loe2 = parseFloat(d.loe2);
        laeloe[1] = lae = lae1 + lae2 / 60; //纬度
        laeloe[0] = loe = loe1 + loe2 / 60; //经度
        convert(laeloe);
    }
}
getGps();
// setInterval(function () {getGps()},3000);