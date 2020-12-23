from module.ccsun import *
from config.configManager import *
from module.cqEncoder import *
from module.timer import RepeatingTimer
from module.functions import *

configManager = Config()
CQEncoder = CQEncoder()
# 运行命令
qq = configManager.config["user"]["qq"]
authKey = configManager.config["user"]["authKey"]
mirai_api_http_locate = configManager.config["user"]["httpapi"]
app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")

ccsunGroup = configManager.config["ccsunGroup"]
sent = False


async def Timer1():
    global sent
    trigger_time = "00:00"
    timeNow = time.strftime('%H:%M', time.localtime(time.time()))
    if timeNow == trigger_time and sent == False:
        sent = True
        try:
            info = CCSUN.sendBandwidth(True)
            await app.sendGroupMessage(ccsunGroup, info)
            pass
        except:
            pass
    if timeNow != trigger_time and sent == True:
        sent = False


t = RepeatingTimer(3, Timer1)
t.start()

CCSUN = CCSUN()

# 运行指令
async def run_command(type: str, data: dict):
    app = data[Mirai]
    if type == "group":
        group = data[Group]
        member = data[Member]
        source = data[Source]
        message = data[MessageChain]

        if group.id == ccsunGroup:
            cqMessage = CQEncoder.messageChainToCQ(message)
            command = commandDecode(cqMessage)
            if cqMessage == "登录":
                CCSUN.Login()
                await app.sendGroupMessage(ccsunGroup, '已登录')
                pass
            if cqMessage == "流量":
                info = CCSUN.sendBandwidth()
                if info.find('Error') != -1:
                    CCSUN.refreshToken()
                    info = CCSUN.sendBandwidth()
                await app.sendGroupMessage(ccsunGroup, info)
            if cqMessage == "订阅":
                info = CCSUN.getSubscribe()
                if info == '':
                    CCSUN.Login()
                    info = CCSUN.getSubscribe()
                    if info == '' : info = '获取数据失败'
                await app.sendGroupMessage(ccsunGroup, info)
            if cqMessage[:2] == "图表":
                if len(cqMessage) >= 2:
                    day = cqMessage[2:]
                    if not is_number(day): day = "7"
                if int(day) > 180:
                    day = "180"
                    await app.sendGroupMessage(ccsunGroup, "最大查询过去180天的数据", quoteSource=source)
                imagePath = CCSUN.getChart(source.id, day)
                await app.sendGroupMessage(ccsunGroup, [Image.fromFileSystem(imagePath)])
                os.remove(imagePath)
            if command[0] == "/ccsun":
                if len(command) >= 1:
                    if command[1] == "update":
                        info = CCSUN.sendBandwidth(True)
                        await app.sendGroupMessage(ccsunGroup, info)
