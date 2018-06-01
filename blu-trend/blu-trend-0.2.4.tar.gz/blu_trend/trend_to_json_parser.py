from datetime import datetime
import time
import json
import re

def daum_trend_to_json(trend_text):
    list = trend_text.split("\n")
    nowtime = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    timelist = nowtime.split(" ")
    ymd = timelist[0].split("-")
    hms = timelist[1].split(":")
    d = datetime(int(ymd[0]), int(ymd[1]), int(ymd[2]), int(hms[0]), int(hms[1]), int(hms[2]))
    unixtime = int(time.mktime(d.timetuple()))
    dic = {}
    dic1 = {}
    for idx in range(0,len(list)):
        # print(idx)
        if(list[idx].find('위') != -1):
            buf = list[idx].split('위')
            if(buf[0].isdigit() and int(buf[0]) > 0 and int(buf[0]) <= 10):
              dic1[int(buf[0])] = list[idx+1]

    dic[unixtime] = dic1
    j = json.dumps(dic, ensure_ascii=False).encode("utf8")
    return dic

def naver_trend_to_json(trend_text):
    list = trend_text.split("\n")
    ymd = list[0].split(".")  # 년월일의 list
    hms = list[1].split(" ")[0].split(":") #시간 분 초 의 list
    d = datetime(int(ymd[0]),int(ymd[1]),int(ymd[2]), int(hms[0]), int(hms[1]),int(hms[2]))
    unixtime = int(time.mktime(d.timetuple()))
    dic = {}
    dic1 = {}
    for idx in range(2,len(list)):
        a = list[idx].split(" ")
        dic1[a[0]]= list[idx].split(a[0]+" ")[1]
    dic[str(unixtime)] = dic1
    j = json.dumps(dic,ensure_ascii=False).encode("utf8")
    return dic


def melon_chart_to_json(melon_chart):
    artist = melon_chart[0]
    title = melon_chart[1]
    link = melon_chart[2]
    nowtime = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    timelist = nowtime.split(" ")
    ymd = timelist[0].split("-")
    hms = timelist[1].split(":")
    d = datetime(int(ymd[0]), int(ymd[1]), int(ymd[2]), int(hms[0]), int(hms[1]), int(hms[2]))
    unixtime = int(time.mktime(d.timetuple()))
    dic = {}
    dic1 = {}
    for idx in range(0,len(artist)):
        dic2 = {}
        dic2['content'] = artist[idx] + " - " + title[idx]
        linkbuf = (re.findall('\d+', link[idx]))
        l = "melonplayer://play?ref=&menuid="+linkbuf[0]+"&cid="+linkbuf[1]
        dic2['link']= l
        dic1[idx+1] = dic2
    dic[str(unixtime)] = dic1
    j = json.dumps(dic, ensure_ascii=False).encode("utf8")
    return dic