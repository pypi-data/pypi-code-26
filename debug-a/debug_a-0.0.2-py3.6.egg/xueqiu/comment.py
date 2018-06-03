# -*- coding: utf-8 -*-

import requests
import time
from bs4 import BeautifulSoup
from debug_a.xueqiu.utils import make_symbol
from debug_a.xueqiu import HOME
from zb.crawlers.utils import get_header


def get_comments(code, sleep=1):
    """获取股票code的雪球评论

    :param float sleep: 睡眠时间， 默认值为 1
    :param str code: 股票代码，如 `600122`
    :return:
    """
    headers = get_header()
    sess = requests.Session()

    # 访问首页，获取cookies
    sess.get(HOME, headers=headers, timeout=10)

    # 获取首页评论
    symbol = make_symbol(code)
    real_time = str(time.time()).replace('.', '')[0:-1]  # 获取当前时间
    comment_url = 'https://xueqiu.com/statuses/search.json?' \
                  'count=10&comment=0&symbol={symbol}&hl=0&' \
                  'source=user&sort=time&page={page}&_={real_time}'
    url = comment_url.format(symbol=symbol, page=1, real_time=real_time)
    res = sess.get(url, headers=headers, timeout=10).json()
    count = res['count']            # 评论总条数
    total_page = res['maxPage']     # 页数
    print("总页数：", total_page)
    # 评论数据存储list
    comments = {
        "symbol": symbol,
        "count": count,
    }
    coms = []
    for i in range(1, total_page+1):
        time.sleep(sleep)
        headers = get_header()
        sess_temp = requests.Session()

        # 访问首页，获取cookies
        sess_temp.get(HOME, headers=headers, timeout=10)
        real_time = str(time.time()).replace('.', '')[0:-1]  # 获取当前时间

        print(i)
        url = comment_url.format(symbol=symbol, page=i, real_time=real_time)
        try:
            res = sess_temp.get(url, headers=headers, timeout=10).json()['list']
        except:
            print(i, "fail")
            continue
        for r in res:
            com = {
                "text": BeautifulSoup(r['text'], 'lxml').text,
                "id": r['id'],
                "time": r['timeBefore'],
                "reply_count": int(r['reply_count']),
                "source": r['source']
            }

            user = {
                "id": r['user']['id'],
                "city": r['user']['city'],
                "description": r['user']['description'],
                "followers_count": r['user']['followers_count'],
                "friends_count": r['user']['friends_count'],
                "gender": r['user']['gender'],
                "nick_name": r['user']['screen_name'],
                "province": r['user']['province'],
                "status_count": r['user']['status_count'],
            }

            com['user'] = user

            if com['reply_count'] > 0:
                com['sub_comments'] = _get_sub_comments(com['id'])
            else:
                com['sub_comments'] = []

            coms.append(com)
    comments['comment_list'] = coms
    return comments


def _get_sub_comments(comment_id):
    """获取评论下面的子评论

    :param str comment_id: 评论id，如 `106580772`
    :return: list sub_comments
    """
    sub_com_url = "https://xueqiu.com/statuses/comments.json?id={comment_id}" \
                  "&count=20&page=1&reply=true&asc=false&type=status&split=true"
    url = sub_com_url.format(comment_id=comment_id)

    headers = get_header()
    sess = requests.Session()

    # 访问首页，获取cookies
    sess.get(HOME, headers=headers, timeout=10)

    res = sess.get(url, headers=headers).json()['comments']
    sub_comments = []

    for r in res:
        com = {
            "timestamp": r['created_at'],
            "ip": r['created_ip'],
            "text": BeautifulSoup(r['text'], 'lxml').text,
            "source": r['source'],
        }

        user = {
            "id": r['user']['id'],
            "city": r['user']['city'],
            "description": r['user']['description'],
            "followers_count": r['user']['followers_count'],
            "friends_count": r['user']['friends_count'],
            "gender": r['user']['gender'],
            "nick_name": r['user']['screen_name'],
            "province": r['user']['province'],
            "status_count": r['user']['status_count'],
        }

        com["user"] = user

        sub_comments.append(com)
    return sub_comments



