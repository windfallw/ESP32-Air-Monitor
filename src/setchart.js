// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

let Area_chart_template = {
    type: 'line',
    data: {
        labels: ['加载中'],
        datasets: []
    },
    options: {
        maintainAspectRatio: false,
        title: {
            display: true,
            text: ''
        },
        scales: {
            xAxes: [{
                ticks: {
                    maxTicksLimit: 5
                },
                gridLines: {
                    drawBorder: true
                },
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: ''
                },
                gridLines: {
                    drawBorder: true,
                    borderDash: [2],
                }
            }],
        },
        legend: {
            display: true,
            labels: {
                boxWidth:30,
                fontSize:9
            },
            position: 'bottom'
        },
        tooltips: {
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            titleMarginBottom: 10,
            titleFontColor: '#6e707e',
            titleFontSize: 14,
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            intersect: false,
            mode: 'index',
            caretPadding: 10,
        }
    }
};

function setAreaChart(ctx, config, title, unit) {
    Area_chart_template.options.title.text = title;
    Area_chart_template.options.scales.yAxes[0].scaleLabel.labelString = unit;
    Area_chart_template.data.datasets = [];
    config.forEach(function (d) {
        Area_chart_template.data.datasets.push({
            label: d.label,
            lineTension: 0,
            backgroundColor: "rgba(78, 115, 223, 0.05)",
            borderColor: d.color,
            pointRadius: 3,
            pointBackgroundColor: d.color,
            pointBorderColor: d.color,
            pointHoverRadius: 3,
            pointHoverBackgroundColor: d.color,
            pointHoverBorderColor: d.color,
            pointHitRadius: 10,
            pointBorderWidth: 2,
            data: [0],
        });
    });
    return new Chart(ctx, Area_chart_template);
}

let AreaChart_select = 0;
let Area_ctx = document.getElementById('AreaChart').getContext("2d");
let Area_Chart = setAreaChart(Area_ctx, [{label: 'CF=1标准颗粒物', color: '#43CBFF'}, {
    label: '大气环境下颗粒物',
    color: '#7367F0'
}], 'PM1.0浓度', 'μg/m3');

let PM1_0CF1 = [];
let PM2_5CF1 = [];
let PM10CF1 = [];
let PM1_0AE = [];
let PM2_5AE = [];
let PM10AE = [];
let Gt0_3um = [];
let Gt0_5um = [];
let Gt1_0um = [];
let Gt2_5um = [];
let Gt5_0um = [];
let Gt10um = [];
let humidity = [];
let temper = [];

let airData;
let time = [];

function addData(chart, label, data) {
    let i = 0;
    chart.data.labels = label;
    chart.data.datasets.forEach(dataset => {
        dataset.data = data[i];
        i++;
    });
    chart.update();
}

function getAir() {
    let now;
    $.ajax({
        type: "get",
        url: "/info/air",
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
        if (airData === JSON.stringify(d)) {
            return;
        }
        airData = JSON.stringify(d);
        //限制长度避免浏览器过卡
        if (time.length >= 50) {
            time.shift();
            PM1_0CF1.shift();
            PM2_5CF1.shift();
            PM10CF1.shift();
            PM1_0AE.shift();
            PM2_5AE.shift();
            PM10AE.shift();
            Gt0_3um.shift();
            Gt0_5um.shift();
            Gt1_0um.shift();
            Gt2_5um.shift();
            Gt5_0um.shift();
            Gt10um.shift();
            humidity.shift();
            temper.shift();
        }
        now = new Date();
        time.push(now.getHours() + ':' + now.getMinutes() + ':' + now.getSeconds());
        PM1_0CF1.push(d.PM1_0CF1);
        PM2_5CF1.push(d.PM2_5CF1);
        PM10CF1.push(d.PM10CF1);
        PM1_0AE.push(d.PM1_0AE);
        PM2_5AE.push(d.PM2_5AE);
        PM10AE.push(d.PM10AE);
        Gt0_3um.push(d.Gt0_3um);
        Gt0_5um.push(d.Gt0_5um);
        Gt1_0um.push(d.Gt1_0um);
        Gt2_5um.push(d.Gt2_5um);
        Gt5_0um.push(d.Gt5_0um);
        Gt10um.push(d.Gt10um);
        humidity.push(d.humidity);
        temper.push(d.temperature);
        if (AreaChart_select === 0) addData(Area_Chart, time, [PM1_0CF1, PM1_0AE]);
        else if (AreaChart_select === 1) addData(Area_Chart, time, [PM2_5CF1, PM2_5AE]);
        else if (AreaChart_select === 2) addData(Area_Chart, time, [PM10CF1, PM10AE]);
        else addData(Area_Chart, time, [Gt0_3um, Gt0_5um, Gt1_0um, Gt2_5um, Gt5_0um, Gt10um]);
    }
}

function switchAreaChart(s) {
    if (s === AreaChart_select) {
    } else if (s === 0) {
        AreaChart_select = 0;
        Area_Chart.destroy();
        Area_Chart = setAreaChart(Area_ctx, [{label: 'CF=1标准颗粒物', color: '#43CBFF'}, {
            label: '大气环境下颗粒物',
            color: '#7367F0'
        }], 'PM1.0浓度', 'μg/m3');
    } else if (s === 1) {
        AreaChart_select = 1;
        Area_Chart.destroy();
        Area_Chart = setAreaChart(Area_ctx, [{label: 'CF=1标准颗粒物', color: '#69FF97'}, {
            label: '大气环境下颗粒物',
            color: '#00E4FF'
        }], 'PM2.5浓度', 'μg/m3');
    } else if (s === 2) {
        AreaChart_select = 2;
        Area_Chart.destroy();
        Area_Chart = setAreaChart(Area_ctx, [{label: 'CF=1标准颗粒物', color: '#F6CEEC'}, {
            label: '大气环境下颗粒物',
            color: '#D939CD'
        }], 'PM10浓度', 'μg/m3');
    } else {
        AreaChart_select = 3;
        Area_Chart.destroy();
        Area_Chart = setAreaChart(Area_ctx, [
            {label: '0.3μm以上颗粒物', color: '#43CBFF'},
            {label: '0.5μm以上颗粒物', color: '#7367F0'},
            {label: '1μm以上颗粒物', color: '#81FBB8'},
            {label: '2.5μm以上颗粒物', color: '#28C76F'},
            {label: '5μm以上颗粒物', color: '#F6CEEC'},
            {label: '10μm以上颗粒物', color: '#D939CD'}], '空气中颗粒物', '0.1L空气中的颗粒物个数');
    }
}

setInterval(getAir, 1000);
