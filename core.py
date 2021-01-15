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

ccsun_group = configManager.config["ccsunGroup"]
write_log("[Notice] CCSUN-Bot已启动", 3)


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
        write_log(info, 0)
    except Exception as e:
        print(e)
        write_log(e, 3)


@scheduler.scheduled_job('cron', hour='0', minute='0', second='0')
def run_timer():
    asyncio.run(auto_update())


Thread(target=scheduler.start).start()


# 更新流量
async def updateBandwidth():
    info = CCSUN.getBandwidthStr(True)
    await app.sendGroupMessage(ccsun_group, info)
    if CCSUN.resetTotal():
        notice = '[Notice]\n今天是月结日,已重置流量。\n上月流量使用情况:\n'
        image_path = CCSUN.getChart("reset", str(days_before_month()))
        await app.sendGroupMessage(ccsun_group,  [Plain(notice), Image.fromFileSystem(image_path)])
        os.remove(image_path)
        write_log(notice + "[图表]", 3)
    return info


# 运行指令
async def run_command(message_type: str, data: dict):
    mirai_app = data[Mirai]
    if message_type == "group":
        group = data[Group]
        member = data[Member]
        source = data[Source]
        message = data[MessageChain]
        if group.id == ccsun_group:
            info = ""
            cq_message = CQEncoder.messageChainToCQ(message)
            write_log(f"[{member.id}]{cq_message}", 1)
            command = commandDecode(cq_message)
            if cq_message == "登录":
                CCSUN.Login()
                info = '[Notice]\n已登录'
                await mirai_app.sendGroupMessage(ccsun_group, info)
            if cq_message == "流量":
                info = CCSUN.getBandwidthStr()
                if info.find('Error') != -1:
                    CCSUN.Login()
                    CCSUN.refreshToken()
                    info = CCSUN.getBandwidthStr()
                await mirai_app.sendGroupMessage(ccsun_group, info)
            if cq_message == "订阅":
                info = CCSUN.getSubscribe()
                if info == '':
                    CCSUN.Login()
                    info = CCSUN.getSubscribe()
                    if info == '':
                        info = '[getSubscribe Error]\n获取数据失败'
                await mirai_app.sendGroupMessage(ccsun_group, info)
            if cq_message[:2] == "图表":
                day = ""
                if len(cq_message) >= 2:
                    day = cq_message[2:]
                    if not is_number(day):
                        day = "7"
                if int(day) > 180:
                    day = "180"
                    info = "[Notice]\n最大查询过去180天的数据"
                    await mirai_app.sendGroupMessage(ccsun_group, info)
                image_path = CCSUN.getChart(str(source.id), day)
                await mirai_app.sendGroupMessage(ccsun_group, [Image.fromFileSystem(image_path)])
                os.remove(image_path)
                info = "[图表]"
            if command[0].lower() == "/ccsun":
                if len(command) >= 1:
                    if command[1].lower() == "update":
                        info = await updateBandwidth()
            write_log(info, 0)


if __name__ == "__main__":
    app.run()
