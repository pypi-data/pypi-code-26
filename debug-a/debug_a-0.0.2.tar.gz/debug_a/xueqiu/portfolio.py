# -*- coding: utf-8 -*-
"""
雪球组合 - 数据获取和分析

入口页：https://xueqiu.com/p/discover

-------------------------组合相关接口-------------------------
排行榜： https://xueqiu.com/cubes/discover/rank/cube/list.json?category=12&count=100&market=cn&profit=monthly_gain&sort=best_benefit
刷选器参数：https://xueqiu.com/cubes/discover/rank/cube/filter.json?

组合评分接口：https://xueqiu.com/cubes/rank/summary.json?symbol=ZH109691&ua=web
调仓： https://xueqiu.com/cubes/rebalancing/show_origin.json?rb_id=39001944&cube_symbol=ZH109691
=========================================================================
"""
import requests
import traceback
from zb.crawlers.utils import get_header
from debug_a.xueqiu import HOME



def get_top_portfolio(market='cn', profit="monthly_gain", count=30):
    """"""
    base_url = "https://xueqiu.com/cubes/discover/rank/cube/list.json?" \
               "category=12&count={count}&market={market}&profit={profit}&sort=best_benefit"
    url = base_url.format(market=market, count=count, profit=profit)
    headers = get_header()
    sess = requests.session()
    sess.get(HOME, headers=headers)
    try:
        res = sess.get(url, headers=headers).json()['list']
    except:
        traceback.print_exc()

    top_pfs = []
    for r in res:
        pf = {
            "name": r['name'],
            "symbol": r['symbol'],
            "description": r['description'],
            "follower_count": r['follower_count'],
            "updated_at": r['updated_at'],
            "net_value": r['net_value'],
            "monthly_gain": str(r['monthly_gain'])+"%",
            "total_gain": str(r['annualized_gain_rate'])+"%",
            "last_rb_id": r['last_rb_id'],
        }

        user = {
            "id": r['owner']['id'],
            "city": r['owner']['city'],
            "description": r['owner']['description'],
            "followers_count": r['owner']['followers_count'],
            "friends_count": r['owner']['friends_count'],
            "gender": r['owner']['gender'],
            "nick_name": r['owner']['screen_name'],
            "province": r['owner']['province'],
            "status_count": r['owner']['status_count'],
        }

        pf['user'] = user

        top_pfs.append(pf)
    return top_pfs


