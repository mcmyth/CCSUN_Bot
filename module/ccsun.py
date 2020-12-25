import datetime
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


def gbUnitConverter(number, unit):
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
    token: str
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

    def updateData(self, date, upload, download, uploaded, downloaded):
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
            token = params['token'][0]
            self.config["token"] = token
            self.saveConfig()
            return token
        except Exception as e:
            return str(f'[refreshToken Error]\n{e}')

    def getBandwidth(self):
        session = requests.session()
        url = f'https://{self.domain}/modules/servers/V2RaySocks/additional-features/flow-scriptable/flow-scriptable.php?sid={self.product}&token={self.token}'
        try:
            res = session.get(url, headers=self.headers, verify=False, allow_redirects=False)
            source = res.content.decode('utf-8')
            source = source.replace(' ', '').replace('Subscription-Userinfo:', '').split(';')
            source.pop()
            config = {}
            for item in source:
                key = item.split('=')[0]
                value = item.split('=')[1]
                config[key] = round(Decimal(value))
            return config
        except Exception as e:
            return str(f'[getBandwidth Error]\n{e}')

    def sendBandwidth(self, update=False):
        try:
            data = self.getBandwidth()
            if data == {}:
                raise Exception('获取数据失败')
            upload = gbUnitConverter(data['upload'], 'byte')
            download = gbUnitConverter(data['download'], 'byte')
            total = gbUnitConverter(data['total'], 'byte')
            yesterdayDownload = self.config["yesterday"]["download"]
            yesterdayUpload = self.config["yesterday"]["upload"]
            usedDownload = round(download - yesterdayDownload, 2)
            usedUpload = round(upload - yesterdayUpload, 2)
            if update == True:
                isUpdate = self.updateData(self.getYesterday(), usedUpload, usedDownload, upload, download)
                self.config["yesterday"]["download"] = download
                self.config["yesterday"]["upload"] = upload
                self.saveConfig()
                info = f'[流量统计 {round(upload + download, 2)}GB / {round(total)}GB] {"" if isUpdate else "(数据库更新失败)"}\n' \
                       f'昨日: ↑{str(usedUpload)}GB  ↓{str(usedDownload)}GB\n' \
                       f'总计: ↑{str(upload)}GB  ↓{str(download)}GB'
            else:
                info = f'[流量统计 {round(upload + download, 2)}GB / {round(total)}GB]\n' \
                       f'当天: ↑{str(usedUpload)}GB  ↓{str(usedDownload)}GB\n' \
                       f'总计: ↑{str(upload)}GB  ↓{str(download)}GB'
            return info
        except Exception as e:
            return str(f'[sendBandwidth Error]\n{e}')

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

                info += f'{client}:{value}+\n'
                i += 1
            info = info[:-1]
            return info
        except Exception as e:
            print(e)
            return str(f'[getSubscribe Error]\n{e}')

    def resetTotal(self):
        day = time.strftime('%d', time.localtime(time.time()))
        if day == self.config["user"]["settlement_day"]:
            self.config["yesterday"]["download"] = "0"
            self.config["yesterday"]["upload"] = "0"
            self.saveConfig()
            return True
        else:
            return False

    def getChart(self, messageid, day="7"):
        with os.popen(f'node module\js\ccsun.js {str(messageid)}.jpg {day}', 'r') as f:
            text = f.read()
        print(text)  # 打印cmd输出结果
        return "temp/" + str(messageid) + ".jpg"

    def __init__(self, init=True):
        self.config = self.loadConfig()
        self.product = self.config["user"]["product"]
        self.token = self.config["token"]
        self.domain = 'z96w.win'
        self.newDatabase()
        if init:
            self.Login()
            self.refreshToken()
