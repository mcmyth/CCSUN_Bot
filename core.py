import asyncio
from threading import Thread
from apscheduler.schedulers.blocking import BlockingScheduler
from config.configManager import *
from module.ccsun import *
from module.cqEncoder import *
from module.functions import *

scheduler = BlockingScheduler()
configManager = Config()
CQEncoder = CQEncoder()
CCSUN = CCSUN(False)

# 运行命令
qq = configManager.config["user"]["qq"]
authKey = configManager.config["user"]["authKey"]
mirai_api_http_locate = configManager.config["user"]["httpapi"]
app = Mirai(f"mirai://{mirai_api_http_locate}?authKey={authKey}&qq={qq}")

ccsunGroup = configManager.config["ccsunGroup"]
write_log("[Notice] CCSUN-Bot已启动")

# 旧方案,Timer 会突然停止运作
# lock = False
# async def auto_update():
#     global lock
#     trigger_time = "00:00"
#     timeNow = time.strftime('%H:%M', time.localtime(time.time()))
#
#     # Log
#     write_log(f"{timeNow} | Lock = {str(lock)}")
#
#     if timeNow == trigger_time and lock == False:
#         lock = True
#         try:
#             info = await updateBandwidth()
#             write_log("[↑]" + info)
#         except Exception as e:
#             print(e)
#             write_log(e)
#     if timeNow != trigger_time and lock == True:
#         lock = False
# from module.timer import RepeatingTimer
# RepeatingTimer(3, auto_update).start()


async def auto_update():
    try:
        info = await updateBandwidth()
        write_log("[↑]" + info)
    except Exception as e:
        print(e)
        write_log(e)


@scheduler.scheduled_job('cron',  hour='0', minute='0', second='0')
def run_timer():
    asyncio.run(auto_update())


Thread(target=scheduler.start).start()


# 更新流量
async def updateBandwidth():
    info = CCSUN.sendBandwidth(True)
    if CCSUN.resetTotal():
        await app.sendGroupMessage(ccsunGroup, '[Notice]\n月结日已重置流量')
    await app.sendGroupMessage(ccsunGroup, info)
    return info


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
            write_log(f"[↓][{member.id}]" + cqMessage)
            command = commandDecode(cqMessage)
            if cqMessage == "登录":
                CCSUN.Login()
                info = '[Notice]\n已登录'
                await app.sendGroupMessage(ccsunGroup, info)
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
                    info = "[Notice]\n最大查询过去180天的数据"
                    await app.sendGroupMessage(ccsunGroup, info)
                imagePath = CCSUN.getChart(source.id, day)
                await app.sendGroupMessage(ccsunGroup, [Image.fromFileSystem(imagePath)])
                os.remove(imagePath)
                info = "发送图表"
            if command[0].lower() == "/ccsun":
                if len(command) >= 1:
                    if command[1].lower() == "update":
                        info = await updateBandwidth()
            write_log("[↑] " + info)

if __name__ == "__main__":
    app.run()