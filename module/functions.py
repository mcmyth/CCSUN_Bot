import re
import time
import calendar
import datetime

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def commandDecode(command):
    regex = r'(\\s*(".+?"|[^:\s])+((\s*:\s*(".+?"|[^\s])+)|)|("(\D|\d)+?^|"(\D|\d)+?"|"+|[^"\s])+)'
    pattern = re.compile(regex)
    c1 = re.findall(pattern, command, flags=0)
    c2 = []
    i = 0
    for x in c1:
        if x[0][0] == '"' and x[0][-1:] == '"':
            c2.append(x[0][1:-1])
        else:
            c2.append(x[0])
        i = i + 1
    return (c2)


def write_log(log, message_type=0):
    # 0为发送消息,1为接收消息
    _type = ""
    if message_type == 0:
        _type = "[↑] "
    elif message_type == 1:
        _type = "[↓] "
    if log != "":
        f = open("ccsun.log", 'a')
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}] {_type}{log}\n")
        f.close()


def days_before_month():
    today = datetime.date.today()
    last_month = today - datetime.timedelta(weeks=4)
    __days_before_month = calendar.monthrange(last_month.year, last_month.month)[1]
    return __days_before_month


sub_task = []


def querySubTask(member, auto_del=False):
    if member in sub_task:
        if auto_del:
            sub_task.pop(sub_task.index(member))
        return True
    else:
        return False


def addSubTask(member):
    if not querySubTask(member):
        sub_task.append(member)
        return True
    else:
        return False
