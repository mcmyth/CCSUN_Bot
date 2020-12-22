import re
from module.dateParse import *

def numOnly(num):
    number = ""
    for x in list(filter(str.isdigit, num)):
        number += x
    return number

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
DateTimeGenerator = DateTimeGenerator()

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
