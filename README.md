# CCSUN Bot

![Python version](https://img.shields.io/badge/Python-3.8.5-blue)
![Node version](https://img.shields.io/badge/Nodejs-14.15.1-brightgreen)

基于Mirai-Python / Nodejs实现

它可以工作在 ~~[ccsun.cc](https://ccsun.cc)(暂不可用)~~ 或 [z96w.win](https://z96w.win)

## 主要功能

* 用于每天0点自动推送CCSUN流量详情
* 获取订阅链接

* 查询流量

* 支持查询过去180天流量数据生成图表

![](https://tu.yaohuo.me/imgs/2020/12/b123f596fe8b18e6.jpg)

![](https://tu.yaohuo.me/imgs/2020/12/40faa0fafb110d99.png)

## 配置
**注: 再此之前请先配置环境依赖**

* 安装Python3及Nodejs
* 安装Python依赖: 在项目路径下执行 ``pip install -r requirements.txt``
* 安装Nodejs依赖: 在项目路径下执行 ``npm i``
* 配置并正确运行mirai-core及*mirai*-http-api
****
需正确配置下列信息到指定文件

``ccsunGroup``填入需要机器人响应的QQ群

``authKey``和``httpapi``填入*mirai*-http-api的密钥和地址

``qq``填入Mirai登录的QQ号码

`config/config.json`

```json
{
  "ccsunGroup": 1000, 
  "user": {
    "authKey": "xxx",
    "httpapi": "xxx",
    "qq": 1000
  }
}
```

***

``username``和``password``填入需要CCSUN后台面板账号密码

``product``填入CCSUN购买的产品id(首页 -> 产品服务 -> 我的服务 -> 进入产品页面 -> 地址栏id=xxx)

``settlement_day``填入月结日,用于月底重置流量

``yesterday``如果没有数据则为0,无需修改

`config/ccsun.json`

```json
{
  "login": {
    "password": "",
    "username": ""
  },
  "user": {
    "product": "1234",
    "settlement_day": "1"
  },
  "yesterday": {
    "download": 0,
    "upload": 0
  }
}
```

## 运行

在项目所在目录 cmd 中执行``python main.py ``

## 指令

1. 流量  **\* 查询当天和总计使用流量**
2. 订阅  **\* 获取订阅链接**
3. 图表 或 图表[天数]  **\*例: 图表15**
4. /ccsun update  **\* 强制提交当天流量到数据库和配置文件**
