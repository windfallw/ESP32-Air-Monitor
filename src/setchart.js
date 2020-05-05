// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

//------------- Area Chart -------------

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
                boxWidth: 30,
                fontSize: 9
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
            pointRadius: 2,
            pointBackgroundColor: d.color,
            pointBorderColor: d.color,
            pointHoverRadius: 3,
            pointHoverBackgroundColor: d.color,
            pointHoverBorderColor: d.color,
        });
    });
    return new Chart(ctx, Area_chart_template);
}

function addData(chart, label, data) {
    let i = 0;
    chart.data.labels = label;
    chart.data.datasets.forEach(dataset => {
        dataset.data = data[i];
        i++;
    });
    chart.update();
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

let AreaChart_select = 0;
let Area_ctx = document.getElementById('AreaChart').getContext("2d");
let Area_Chart = setAreaChart(Area_ctx, [{label: 'CF=1标准颗粒物', color: '#43CBFF'}, {
    label: '大气环境下颗粒物',
    color: '#7367F0'
}], 'PM1.0浓度', 'μg/m3');

//------------- Area Chart -------------

//------------- Pie Chart -------------

let Pie_ctx = document.getElementById("PieChart").getContext("2d");
let Pie_Chart = new Chart(Pie_ctx, {
    type: 'doughnut',
    data: {
        labels: ["湿度", "温度"],
        datasets: [{
            data: [],
            backgroundColor: ['#52E5E7', '#EA5455'],
            hoverBackgroundColor: ['#130CB7', '#FEB692'],
            hoverBorderColor: "rgba(234, 236, 244, 1)",
        }]
    },
    options: {
        maintainAspectRatio: false,
        animation: {
            animateScale: true
        },
        tooltips: {
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            caretPadding: 10,
        },
        legend: {
            display: true
        },
        cutoutPercentage: 75,
    },
});

function updatePieChart(chart, data) {
    chart.data.datasets[0].data = data;
    chart.update();
    $('#humidity').text('湿度: ' + data[0] + '%');
    if (data[1] > 32) {
        let i = $('#temper');
        i.attr('class', 'fas fa-temperature-high text-danger');
        i.text('温度: ' + data[1] + '℃');
    } else $('#temper').text('温度: ' + data[1] + '℃');
}

//------------- Pie Chart -------------

//------------- ajax request -------------

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

function getAir() {
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
        let now = new Date();
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
        updatePieChart(Pie_Chart, [d.humidity, d.temperature]);
        if (AreaChart_select === 0) addData(Area_Chart, time, [PM1_0CF1, PM1_0AE]);
        else if (AreaChart_select === 1) addData(Area_Chart, time, [PM2_5CF1, PM2_5AE]);
        else if (AreaChart_select === 2) addData(Area_Chart, time, [PM10CF1, PM10AE]);
        else addData(Area_Chart, time, [Gt0_3um, Gt0_5um, Gt1_0um, Gt2_5um, Gt5_0um, Gt10um]);
    }
}

//------------- ajax request -------------

setInterval(getAir, 3000);

//------------- Bar Chart -------------

let Bar_ctx = document.getElementById("BarChart").getContext("2d");
let Bar_Chart = new Chart(Bar_ctx, {
    type: 'horizontalBar',
    data: {
        labels: ['VOC模块'],
        datasets: [{
            label: "ECO₂(ppm)",
            backgroundColor: 'rgba(255, 99, 132,0.5)',
            borderColor: 'rgba(255, 99, 132,1)',
            borderWidth:2,
            data: [],
        }, {
            label: "VOC(ppb)",
            backgroundColor: 'rgba(54, 162, 235,0.5)',
            borderColor: 'rgba(54, 162, 235,1)',
            borderWidth:2,
            data: [],
        }, {
            label: "CH₂O(ppb)",
            backgroundColor: 'rgba(255, 159, 64,0.5)',
            borderColor: 'rgba(255, 159, 64,1)',
            borderWidth:2,
            data: [],
        }]
    },
    options: {
        maintainAspectRatio: false,
        scales: {
            xAxes: [{
                gridLines: {
                    display: true,
                    drawBorder: true
                }
            }],
            yAxes: [{
                gridLines: {
                    color: "rgb(234, 236, 244)",
                    zeroLineColor: "rgb(234, 236, 244)",
                    drawBorder: true,
                    borderDash: [2],
                    zeroLineBorderDash: [2]
                }
            }],
        },
        legend: {
            display: true
        },
        tooltips: {
            titleMarginBottom: 10,
            titleFontColor: '#6e707e',
            titleFontSize: 14,
            backgroundColor: "rgb(255,255,255)",
            bodyFontColor: "#858796",
            borderColor: '#dddfeb',
            borderWidth: 1,
            xPadding: 15,
            yPadding: 15,
            displayColors: false,
            caretPadding: 10,
        },
    }
});

function updateBarChart(chart, data) {
    chart.data.datasets[0].data = [data[0]];
    chart.data.datasets[1].data = [data[1]];
    chart.data.datasets[2].data = [data[2]];
    chart.update();
}

let ECO2 = [];//Embodied Carbon ECO2是与产品制造及其成分有关的具体二氧化碳。 ppm浓度（parts per million） 百万分比浓度
let VOC = [];//挥发性有机化合物 ppb（parts per billion）十亿分比浓度
let CH2O = [];//甲醛 ppb（parts per billion） 十亿分比浓度
let vocData;

function getVoc() {
    $.ajax({
        type: "get",
        //   url: "/info/voc",
        url: "https://my-iot.site/info/voc",
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
        if (vocData === JSON.stringify(d)) {
            return;
        }
        if (ECO2.length >= 50) {
            ECO2.shift();
            VOC.shift();
            CH2O.shift();
        }
        vocData = JSON.stringify(d);
        ECO2.push(d.CO2);
        VOC.push(d.VOC);
        CH2O.push(d.CH2O);
        updateBarChart(Bar_Chart, [d.CO2, d.VOC, d.CH2O]);
    }
}

//------------- Bar Chart -------------

setInterval(getVoc, 3000);