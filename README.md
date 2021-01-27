# CCSUN Bot

![Python version](https://img.shields.io/badge/Python-3.8.5-blue)
![Node version](https://img.shields.io/badge/Nodejs-14.15.1-brightgreen)

基于Mirai-Python / Nodejs实现

> [Mirai是什么?](https://github.com/mamoe/mirai/blob/dev/README.md)

CCSUN Bot可以工作在 ~~[ccsun.cc](https://ccsun.cc)(暂不可用)~~ 或 [z96w.win](https://z96w.win)

\* 需使用系统端口`8881`(用于Flask服务端)和`55004`(用于连接mirai-api-http),请留意端口是否已被占用

## 主要功能

* 每天0点自动推送昨天流量详情
* 获取订阅链接
* 查询实时流量以及当天已用流量
* 支持查询过去180天以及实时流量数据生成图表

![示例](https://tu.yaohuo.me/imgs/2020/12/b123f596fe8b18e6.jpg)

![图表](https://tu.yaohuo.me/imgs/2020/12/40faa0fafb110d99.png)

## 配置
**注: 再此之前请先配置环境依赖**

* 安装Python3及Nodejs
* 安装Python依赖: 在项目所在目录中执行命令 ``pip install -r requirements.txt``
* 安装Nodejs依赖: 在项目所在目录中执行命令 ``npm i``
* 配置并正确运行Mirai服务端 (推荐使用 ~~[Mirai Console Loader](https://github.com/iTXTech/mirai-console-loader) 发图有问题~~  mirai-console-wrapper 1.3)
* 安装[mirai-api-http](https://github.com/project-mirai/mirai-api-http)插件
  * 在`setting.yml`中配置端口为`55004` (此处对应配置文件`config/config.json`中的`httpapi`,可自定义)
  * 在`setting.yml`中配置`authKey`密钥
****
需正确配置下列信息到指定文件

``ccsunGroup``填入需要机器人响应的QQ群

``authKey``填入*mirai*-http-api的密钥

 ``httpapi``填入*mirai*-http-api的地址

``qq``填入Mirai登录的QQ号码

`config/config.json`

```json
{
  "ccsunGroup": 1000, 
  "user": {
    "authKey": "xxx",
    "httpapi": "localhost:55004/ws",
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

* 正确安装Python3.8/NodeJS以及所有依赖
* 确保Mirai及mirai-api-http配置正确并已运行
* 在项目所在目录中执行命令``ccsun-bot ``

## 指令

1. 流量  **\* 查询当天和总计使用流量**
2. 订阅  **\* 获取订阅链接**
3. 图表 或 图表[天数]  **\*渲染指定天数的图表(不填数字默认为7天)  例: 图表15**
4. 离线图表 或 离线图表[天数]  **\*只读取数据库中的流量记录渲染图表,不获取实时流量数据** 
5. /ccsun update  **\* 强制提交当天流量到数据库和配置文件**
