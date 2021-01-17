import sqlite3, sys, socket, json
sys.path.append('..')
from flask import Flask, request, render_template, url_for
from flask_cors import *

webApp = Flask(__name__)
CORS(webApp, resources=r'/*')


@webApp.route('/api/ccsun')
def _ccsunAPI():
    args = request.args
    if 'day' in args:
        day = args["day"]
        if day == "": day = "7"
    else:
        day = "7"
    configPath = "config/"
    conn = sqlite3.connect(f'{configPath}data.db')
    cur = conn.cursor()
    query = f"SELECT * FROM ccsun WHERE date < DATE('now', '1 day') and date >= DATE('now', '-{str(day)} day')"
    result = list(cur.execute(query))
    conn.commit()
    conn.close()
    jsonObj = {
        "data": [],
        "status": "ok",
    }
    if len(result) > 0:
        for x in result:
            # id = x[0]
            date = x[1]
            upload = x[2]
            download = x[3]
            uploaded = x[4]
            downloaded = x[5]
            jsonObj["data"].append({
                "date": date,
                "upload": upload,
                "download": download,
                "used": {
                    "upload": uploaded,
                    "download": downloaded
                }
            })
    else:
        jsonObj["status"] = "void"

    return json.dumps(jsonObj)


@webApp.route('/chart')
def _chart() -> str:
    url_for('static', filename='js/ccsun.js')
    url_for('static', filename='js/highcharts.js')
    url_for('static', filename='js/zepto.min.js')
    return render_template('chart.htm')


def net_is_used(port, ip='127.0.0.1'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        s.shutdown(2)
        print('%s:%d is used' % (ip, port))
        return True
    except:
        # print('%s:%d is unused' % (ip, port))
        return False


def run_server():
    port = 8881
    if not net_is_used(port):
        webApp.run(debug=True, use_reloader=False, port=port, threaded=True)
    else:
        print(f"{port}端口已被占用")
