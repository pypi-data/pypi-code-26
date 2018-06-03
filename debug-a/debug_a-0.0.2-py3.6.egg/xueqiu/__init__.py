# -*- coding: utf-8 -*-
"""
行情接口： https://xueqiu.com/v4/stock/quote.json?code=SH600122
分钟级行情： https://xueqiu.com/stock/forchart/stocklist.json?symbol=SH600122&period=1d&one_min=1
个股关注用户列表： https://xueqiu.com/recommend/pofriends.json?type=1&code=SH600122&start=0&count=100
盘口接口：https://xueqiu.com/stock/pankou.json?symbol=SH600122
子评论接口：https://xueqiu.com/statuses/comments.json?id=106580772&count=20&page=1&reply=true&asc=false&type=status&split=true

-----------------组合相关接口-------------------------
排行榜： https://xueqiu.com/cubes/discover/rank/cube/list.json?category=12&count=100&market=cn&profit=monthly_gain
刷选器参数：https://xueqiu.com/cubes/discover/rank/cube/filter.json?

组合评分接口：https://xueqiu.com/cubes/rank/summary.json?symbol=ZH109691&ua=web
调仓： https://xueqiu.com/cubes/rebalancing/show_origin.json?rb_id=39001944&cube_symbol=ZH109691

"""

HOME = "https://xueqiu.com/"


from debug_a.xueqiu.comment import get_comments
from debug_a.xueqiu.portfolio import get_top_portfolio
from debug_a.xueqiu.utils import open_xueqiu



