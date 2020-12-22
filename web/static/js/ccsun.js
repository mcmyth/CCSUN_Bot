const defer = $.Deferred();
const _r = function () {
    $.ajax({
        url: 'http://127.0.0.1:8081/api/ccsun?day=' + GetQueryString("day"),
        success: function (result) {
            defer.resolve(result);
        }
    });
    return defer.promise();
};
$.when(_r()).done(function (result) {
    loaded(JSON.parse(result));
});

function loaded(json_src) {
    const plotOptions = {
        line: {
            dataLabels: {
                enabled: true
            },
            series: {
                animation: false
            }
        }
    }
    const chart1 = Highcharts.chart('container', {
        chart: {
            type: 'line'
        },
        credits: {enabled: false},
        title: {
            text: '当日流量'
        },
        subtitle: {
            text: ''
        },
        xAxis: {},
        yAxis: {
            title: {
                text: '流量 (GB)'
            }
        },
        plotOptions
    });
    let download;
    let upload;
    let date;
    date = download = upload = [];
    for (let i = 0; i < json_src["data"].length; i++) {
        date.push(json_src["data"][i]["date"]);
        chart1.xAxis[0].setCategories(date);
        download.push(parseFloat(json_src["data"][i]["download"]));
        upload.push(parseFloat(json_src["data"][i]["upload"]));
    }

    chart1.addSeries({
        name: '下载',
        data: download
    });
    chart1.addSeries({
        name: '上传',
        data: upload
    });

    const chart2 = Highcharts.chart('container2', {
        chart: {
            type: 'line'
        },
        credits: {enabled: false},
        title: {
            text: '总计流量'
        },
        subtitle: {
            text: ''
        },
        xAxis: {},
        yAxis: {
            title: {
                text: '流量 (GB)'
            }
        },
        plotOptions
    });

    date = download = upload = [];
    for (let i = 0; i < json_src["data"].length; i++) {
        date.push(json_src["data"][i]["date"]);
        chart2.xAxis[0].setCategories(date);
        download.push(parseFloat(json_src["data"][i]["used"]["download"]));
        upload.push(parseFloat(json_src["data"][i]["used"]["upload"]));
    }
    chart2.addSeries({
        name: '下载',
        data: download
    });
    chart2.addSeries({
        name: '上传',
        data: upload
    });
}

function GetQueryString(name) {
    let reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    let r = window.location.search.substr(1).match(reg); //获取url中"?"符后的字符串并正则匹配
    let context = "";
    if (r != null)
        context = r[2];
    reg = null;
    r = null;
    return context == null || context === "" || context === "undefined" ? "" : context;
}