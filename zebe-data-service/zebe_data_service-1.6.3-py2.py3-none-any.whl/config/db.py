# -*- coding: utf-8 -*-
"""
    zebe.config.db
    ~~~~~~~~~~~~~~~~

    数据库配置

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

import os

prefix = ''
if os.name == 'posix':  # Mac
    prefix = '/usr/zebe/'
elif os.name == 'linux':  # Linux
    prefix = '/home/data/'
elif os.name == 'nt':  # Windows
    prefix = 'D:/database/sqlite/'

WECHAT_DB = prefix + 'zebe-wechat.sqlite'  # 微信
PROJECT_DB = prefix + 'zebe-project.sqlite'  # 项目
MEMCARD_DB = prefix + 'zebe-memcard.sqlite'  # 秒记卡 TODO 合并到【记忆】
REMIND_DB = prefix + 'zebe-remind.sqlite'  # 提醒
BLOG_DB = prefix + 'zebe-blog.sqlite'  # 博客
DIARY_DB = prefix + 'zebe-diary.sqlite'  # 日记
AD_DB = prefix + 'zebe-ad.sqlite'  # 广告
APP_DB = prefix + 'zebe-app.sqlite'  # 应用
USER_DB = prefix + 'zebe-user.sqlite'  # 用户
MEMORY_DB = prefix + 'zebe-memory.sqlite'  # 记忆
ENGLISH_DB = prefix + 'zebe-english.sqlite'  # 英语
CDRVBA_DB = prefix + 'zebe-cdrvba.sqlite'  # cdrvba
