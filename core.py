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


# 提交当天流量数据
async def auto_update():
    try:
        info = await updateBandwidth()
        write_log(info, 0)
    except Exception as e:
        print(e)
        write_log(e, 3)


# 每日0点定时任务
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
        image_path = CCSUN.getChart("reset", str(days_before_month()), False)
        await app.sendGroupMessage(ccsun_group, [Plain(notice), Image.fromFileSystem(image_path)])
        os.remove(image_path)
        write_log(notice + "[图表]", 3)
    return info


# 运行指令
async def run_command(message_type: str, data: dict):
    group = data[Group]
    if group.id != ccsun_group or message_type != "group":
        return
    mirai_app = data[Mirai]
    member = data[Member]
    source = data[Source]
    message = data[MessageChain]

    info = ""
    cq_message = CQEncoder.messageChainToCQ(message)
    write_log(f"[{member.id}]{cq_message}", 1)
    command = commandDecode(cq_message)
    # 订阅回复检测
    if is_number(cq_message) and querySubTask(member.id, True):
        cq_message = f'订阅{cq_message}'
    else:
        querySubTask(member.id, True)
    # 登录指令
    if cq_message == "登录":
        CCSUN.Login()
        CCSUN.refreshToken()
        info = '[Notice]\n已登录并刷新Token'
        await mirai_app.sendGroupMessage(ccsun_group, info)
    # 流量指令
    if cq_message == "流量":
        info = CCSUN.getBandwidthStr()
        if info.find('Error') != -1:
            CCSUN.Login()
            CCSUN.refreshToken()
            info = CCSUN.getBandwidthStr()
        await mirai_app.sendGroupMessage(ccsun_group, info)
    # 订阅指令
    if cq_message[:2] == "订阅":
        keyword_len = 2
        num = None
        # 字数大于2并且后面的内容为数字则获取订阅链接
        if len(cq_message) > keyword_len:
            num = cq_message[keyword_len:]
            if not is_number(num): return
            if is_number(num): info = CCSUN.getSubscribeForMenu(num)
        else:
            # 获取订阅菜单
            info = CCSUN.getSubscribeForMenu()
        # 获取失败重试一次
        if info == '':
            CCSUN.Login()
            info = CCSUN.getSubscribeForMenu(num)
        info = info if info != '' else '[getSubscribeForMenu Error]\n获取数据失败'
        await mirai_app.sendGroupMessage(ccsun_group, info, quoteSource=source if num is not None else None)
        if 'Error' not in info: addSubTask(member.id)
    # 图表指令
    if cq_message[:2] == "图表" or cq_message[:4] == "离线图表":
        is_offline = True if cq_message[:2] == "图表" else False
        keyword_len = 2 if cq_message[:2] == "图表" else 4
        day = ""
        # 获取指令后面的数字,如没有则默认为7
        if len(cq_message) >= keyword_len:
            day = cq_message[keyword_len:]
            if not is_number(day):
                day = "7"
        # 不允许大于180天的请求
        if int(day) > 180:
            day = "180"
            info = "[Notice]\n最大查询过去180天的数据"
            await mirai_app.sendGroupMessage(ccsun_group, info)
        # 获取图表
        image_path = CCSUN.getChart(str(source.id), day, is_offline)
        # 获取失败重试一次
        if image_path == '': image_path = CCSUN.getChart(str(source.id), day, is_offline)
        # 获取成功发送图表,失败则提示
        if image_path != '':
            await mirai_app.sendGroupMessage(ccsun_group, [Image.fromFileSystem(image_path)])
            os.remove(image_path)
            info = "[图表]"
        else:
            await mirai_app.sendGroupMessage(ccsun_group, "[getChart Error] 获取图表失败")
    # ccsun指令集
    if command[0].lower() == "/ccsun":
        # 强制提交当天流量数据
        if len(command) >= 1:
            if command[1].lower() == "update": info = await updateBandwidth()
    write_log(info, 0)


if __name__ == "__main__":
    app.run()
