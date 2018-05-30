from datetime import datetime
import time
import json

def naver_trend_to_json(trend_text):
    list = trend_text.split("\n")
    ymd = list[0].split(".")  # 년월일의 list
    hms = list[1].split(" ")[0].split(":"); #시간 분 초 의 list
    d = datetime(int(ymd[0]),int(ymd[1]),int(ymd[2]), int(hms[0]), int(hms[1]),int(hms[2].split(" ")[0]))
    unixtime = int(time.mktime(d.timetuple()))
    dic = {}
    dic1 = {}
    for idx in range(2,len(list)):
        a = list[idx].split(" ")
        # print(a)
        dic1[a[0]]= list[idx].split(a[0]+" ")[1]

    dic[str(unixtime)] = dic1
    j = json.dumps(dic,ensure_ascii=False)
    return j