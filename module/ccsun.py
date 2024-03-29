import datetime
import re
import time
import os
import json
import sqlite3
from decimal import Decimal
from urllib import parse
from bs4 import BeautifulSoup
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def gbUnitConverter(number: float, unit: str):
    unit = unit.lower()
    decimal = 2
    if unit == 'mb':
        return round(number / 1024, decimal)
    elif unit == 'byte':
        for i in range(3):
            number = number / 1024
        return round(number, decimal)
    else:
        return round(number, decimal)


class CCSUN:
    token: str
    product: str
    domain: str
    configPath: str
    config: str
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/55.0.2883.95 Safari/537.36 '
    }

    configPath = "config/"

    def getYesterday(self):
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        return yesterday

    def newDatabase(self):
        if os.path.isfile(f"{self.configPath}data.db"):
            return
        conn = sqlite3.connect(f'{self.configPath}data.db')
        cur = conn.cursor()
        cur.execute('''
CREATE TABLE "ccsun" (
  "id" integer NOT NULL,
  "date" date(255),
  "upload" TEXT(255),
  "download" TEXT(255),
  "uploaded" TEXT(255),
  "downloaded" TEXT(255),
  PRIMARY KEY ("id"),
  CONSTRAINT "date" UNIQUE ("date" ASC)
)''')
        conn.close()
        print('[Notice] New database created')

    def updateData(self, date: datetime, upload: float, download: float, uploaded: float, downloaded: float):
        conn = sqlite3.connect(f'{self.configPath}data.db')
        cur = conn.cursor()
        cur.execute('insert into `ccsun`(`date`, `upload`, `download`, `uploaded`, `downloaded`) VALUES(?,?,?,?,?)',
                    (date, upload, download, uploaded, downloaded))
        conn.commit()
        if cur.rowcount == 0:
            conn.close()
            return False
        else:
            conn.close()
            return True

    def loadConfig(self):
        f = open(f'{self.configPath}ccsun.json', 'r')
        config = json.loads(f.read())
        f.close()
        return config

    def saveConfig(self):
        f = open(f'{self.configPath}ccsun.json', 'w')
        f.write(str(json.dumps(self.config, sort_keys=True, indent=2)))
        f.close()

    def Login(self):
        session = requests.session()
        url = f'https://{self.domain}/dologin.php'
        res = session.post(url, data=self.config["login"], headers=self.headers, verify=False, allow_redirects=False)
        cookies = res.cookies
        cookie = requests.utils.dict_from_cookiejar(cookies)
        self.config["cookie"] = cookie
        print("[CCSUN Login]" + str(cookie))
        self.saveConfig()
        return cookie

    def refreshToken(self):
        session = requests.session()
        try:
            url = f'https://{self.domain}/clientarea.php?action=productdetails&id={self.product}'
            res = session.get(url, headers=self.headers, cookies=self.config["cookie"], verify=False,
                              allow_redirects=False)
            html = res.content.decode('utf-8')
            soup = BeautifulSoup(html, "lxml")
            link = soup.select(".add-renew-notice")[0]['href']
            params = parse.parse_qs(parse.urlparse(link).query)
            self.token = params['token'][0]
            self.config["token"] = self.token
            self.saveConfig()
            return self.token
        except Exception as e:
            return str(f'[refreshToken Error]\n{e}')

    def getBandwidthData(self):
        session = requests.session()
        url = f'https://{self.domain}/modules/servers/V2RaySocks/additional-features/flow-scriptable/flow-scriptable.php?sid={self.product}&token={self.token}'
        try:
            res = session.get(url, headers=self.headers, verify=False, timeout=1500)
            source = res.content.decode('utf-8')
            source = source.replace(' ', '').replace('Subscription-Userinfo:', '').split(';')
            source.pop()
            config = {}
            print(f'[getBandwidthData] { source }')
            for item in source:
                key = item.split('=')[0]
                value = item.split('=')[1]
                config[key] = round(Decimal(value))
            return config
        except Exception as e:
            print(e)
            return str(f'[getBandwidthData Error]\n{e}')

    def getBandwidthStr(self, update: bool = False):
        try:
            data = self.getBandwidthData()
            if data == {}:
                raise Exception('获取流量数据失败')
            upload = gbUnitConverter(data['upload'], 'byte')
            download = gbUnitConverter(data['download'], 'byte')
            total = gbUnitConverter(data['total'], 'byte')
            yesterday_download = self.config["yesterday"]["download"]
            yesterday_upload = self.config["yesterday"]["upload"]
            used_download = round(float(download) - float(yesterday_download), 2)
            used_upload = round(float(upload) - float(yesterday_upload), 2)
            if update:
                is_update = self.updateData(self.getYesterday(), used_upload, used_download, upload, download)
                self.config["yesterday"]["download"] = download
                self.config["yesterday"]["upload"] = upload
                self.saveConfig()
                info = f'[流量统计 {round(upload + download, 2)}GB / {round(total)}GB] {"" if is_update else "(数据库更新失败)"}\n' \
                       f'昨日: ↑{str(used_upload)}GB  ↓{str(used_download)}GB\n' \
                       f'总计: ↑{str(upload)}GB  ↓{str(download)}GB\n' \
                       f'---------------\n' \
                       f'剩余流量: {round(total - (upload + download), 2)}GB'
            else:
                info = f'[流量统计 {round(upload + download, 2)}GB / {round(total)}GB]\n' \
                       f'当天: ↑{str(used_upload)}GB  ↓{str(used_download)}GB\n' \
                       f'总计: ↑{str(upload)}GB  ↓{str(download)}GB\n' \
                       f'---------------\n' \
                       f'剩余流量: {round(total - (upload + download), 2)}GB'
            return info
        except Exception as e:
            return str(f'[getBandwidthStr Error]\n{e}')

    def getSubscribeForMenu(self, num=None):
        session = requests.session()
        url = f'https://{self.domain}/clientarea.php?action=productdetails&id={self.product}'
        try:
            res = session.get(url, headers=self.headers, cookies=self.config["cookie"], verify=False,
                              allow_redirects=False)
            html = res.content.decode('utf-8')
            soup = BeautifulSoup(html, "lxml")
            client_label = soup.find_all("div", {"class": "subscribe-label", "style": None})
            subscribe_group = soup.find_all("div", {"class": "subscribe-group", "style": None})
            i = 0
            info = ''
            if num is None:
                for item in subscribe_group:
                    _client_label = client_label[i].get_text().replace(' ', '').replace('\n', '')
                    if len(_client_label) >= 4:
                        _client_label = list(_client_label)
                        _client_label[3] = '*'
                        _client_label[4] = '*'
                        _client_label = ''.join(_client_label)
                    info += f'[{i + 1}]{_client_label}\n'
                    i += 1
                info = '' if info[:-1] == '' else '请回复数字获取链接\n' + info[:-1]
            else:
                num = int(num) - 1
                if len(subscribe_group) > num >= 0:
                    info = subscribe_group[num].get_text()
                    links = re.search('https?:\/\/[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', info)
                    info = links[0]
                else:
                    if not len(subscribe_group) == 0:
                        info = '该订阅不存在,如需获取订阅列表请回复"订阅"!'
            return info
        except Exception as e:
            print(e)
            return str(f'[getSubscribeForMenu Error]\n{e}')

    def getSubscribe(self):
        session = requests.session()
        url = f'https://{self.domain}/clientarea.php?action=productdetails&id={self.product}'
        try:
            res = session.get(url, headers=self.headers, cookies=self.config["cookie"], verify=False,
                              allow_redirects=False)
            html = res.content.decode('utf-8')
            soup = BeautifulSoup(html, "lxml")
            source = soup.select("div.subscribe-linktext")
            # subscribe_link = {}
            i = 0
            info = ''
            for item in source:
                value = item.get_text().replace(' ', '').replace('\n', '')
                client = item['id']

                # Fix existing error in the source code
                if value.find('loon') != -1:
                    client = 'Loon'

                # Add to object
                # subscribe_link[i] = {}
                # subscribe_link[i]["link"] = value
                # subscribe_link[i]["client"] = type

                info += f'{client}:{value}\n'
                i += 1
            info = info[:-1]
            return info
        except Exception as e:
            print(e)
            return str(f'[getSubscribe Error]\n{e}')

    def resetTotal(self):
        day = time.strftime('%d', time.localtime(time.time()))
        if day == self.config["user"]["settlement_day"]:
            self.config["yesterday"]["download"] = 0
            self.config["yesterday"]["upload"] = 0
            self.saveConfig()
            return True
        else:
            return False

    def getChart(self, filename: str, day: str = "7", online: bool = True):
        with os.popen(f'node module/js/ccsun.js {str(filename)}.jpg {day} {"online" if online else "offline"}', 'r') as f:
            text = f.read()
            if text != "":
                print(text)  # 查错用,打印终端输出结果
        filename = "./temp/" + filename + ".jpg"
        if os.path.exists(filename):
            return filename
        else:
            return ''

    def __init__(self, init: bool = True):
        self.config = self.loadConfig()
        self.product = self.config["user"]["product"]
        self.token = self.config["token"]
        self.domain = 'z96w.win'
        self.newDatabase()
        if init:
            self.Login()
            self.refreshToken()
