const port = '8881'
$(function () {
    $.ajax({
        type: "GET",
        contentType: "application/json;charset=UTF-8",
        url: `http://127.0.0.1:${port}/api/ccsun${window.location.search}`,
        success: function (result) {
            loaded(JSON.parse(result));
        }
    });
});

function loaded(json_src) {
    let notice = ''
    if(json_src["status"] === "data_acquisition_failed") {
        notice = "获取实时流量数据失败"
    }
    const plotOptions = {
        line: {
            animation: false,
            dataLabels: {
                enabled: true
            }
        }
    }
    const chart1 = Highcharts.chart('container', {
        chart: {
            type: 'line',
            animation: false
        },
        credits: {enabled: false},
        title: {
            text: '当日流量'
        },
        subtitle: {
            text: notice
        },
        xAxis: {},
        yAxis: {
            title: {
                text: '流量 (GB)'
            }
        },
        plotOptions
    });
    let date = [];
    let download = [];
    let upload = [];
    // let toal = 0;
    for (let i = 0; i < json_src["data"].length; i++) {
        const _date = json_src["data"][i]["date"].slice(5)
        date.push(_date);
        chart1.xAxis[0].setCategories(date);
        let _download = parseFloat(json_src["data"][i]["download"]);
        let _upload = parseFloat(json_src["data"][i]["upload"]);
        download.push(_download);
        upload.push(_upload);
        // toal += _download + _upload
    }
    // chart1.setTitle(null, { text: `合计:${String(toal.toFixed(2))}GB`});
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
            type: 'line',
             animation: false
        },
        credits: {enabled: false},
        title: {
            text: '总计流量'
        },
        subtitle: {
            text: notice
        },
        xAxis: {},
        yAxis: {
            title: {
                text: '流量 (GB)'
            }
        },
        plotOptions
    });

    date = [];
    download = [];
    upload = [];
    // toal = 0;
    for (let i = 0; i < json_src["data"].length; i++) {
        const _date = json_src["data"][i]["date"].slice(5)
        date.push(_date);
        chart2.xAxis[0].setCategories(date);
        let _download = parseFloat(json_src["data"][i]["used"]["download"]);
        let _upload = parseFloat(json_src["data"][i]["used"]["upload"]);
        download.push(_download);
        upload.push(_upload);
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

/*
function GetQueryString(name) {
    let reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    let r = window.location.search.substr(1).match(reg); //获取url中"?"符后的字符串并正则匹配
    let context = "";
    if (r != null)
        context = r[2];
    reg = null;
    r = null;
    return context == null || context == "" || context == "undefined" ? "" : context;
}*/
