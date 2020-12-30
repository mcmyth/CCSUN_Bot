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
lock = False


async def Timer1():
    global lock
    trigger_time = "00:00"
    timeNow = time.strftime('%H:%M', time.localtime(time.time()))

    # Log
    f = open("ccsun.log", 'a')
    log = f"{trigger_time} | {timeNow} | Lock = {str(lock)}"
    f.write(log)
    f.close()

    if timeNow == trigger_time and lock == False:
        lock = True
        try:
            await updateBandwidth()
        except Exception as e:
            print(e)
            write_log(f"{trigger_time} | {timeNow} | Lock = {str(lock)}")
    if timeNow != trigger_time and lock == True:
        lock = False


t = RepeatingTimer(3, Timer1)
t.start()

CCSUN = CCSUN(False)


# 更新流量
async def updateBandwidth():
    info = CCSUN.sendBandwidth(True)
    if CCSUN.resetTotal():
        await app.sendGroupMessage(ccsunGroup, '[Notice]\n月结日已重置流量')
    await app.sendGroupMessage(ccsunGroup, info)


# 运行指令
async def run_command(type: str, data: dict):
    app = data[Mirai]
    if type == "group":
        group = data[Group]
        member = data[Member]
        source = data[Source]
        message = data[MessageChain]
        if group.id == ccsunGroup:
            info = ""
            cqMessage = CQEncoder.messageChainToCQ(message)
            command = commandDecode(cqMessage)
            if cqMessage == "登录":
                CCSUN.Login()
                await app.sendGroupMessage(ccsunGroup, '[Notice]\n已登录')
            if cqMessage == "流量":
                info = CCSUN.sendBandwidth()
                if info.find('Error') != -1:
                    CCSUN.Login()
                    CCSUN.refreshToken()
                    info = CCSUN.sendBandwidth()
                await app.sendGroupMessage(ccsunGroup, info)
            if cqMessage == "订阅":
                info = CCSUN.getSubscribe()
                if info == '':
                    CCSUN.Login()
                    info = CCSUN.getSubscribe()
                    if info == '' : info = '[getSubscribe Error]\n获取数据失败'
                await app.sendGroupMessage(ccsunGroup, info)
            if cqMessage[:2] == "图表":
                if len(cqMessage) >= 2:
                    day = cqMessage[2:]
                    if not is_number(day): day = "7"
                if int(day) > 180:
                    day = "180"
                    await app.sendGroupMessage(ccsunGroup, "[Notice]\n最大查询过去180天的数据")
                imagePath = CCSUN.getChart(source.id, day)
                await app.sendGroupMessage(ccsunGroup, [Image.fromFileSystem(imagePath)])
                os.remove(imagePath)
            if command[0].lower() == "/ccsun":
                if len(command) >= 1:
                    if command[1].lower() == "update":
                        await updateBandwidth()
            write_log(info)
