# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

REQUEST_STATUS_CANCEL = 0
REQUEST_STATUS_REQUEST = 1
REQUEST_STATUS_QUOTE = 2
REQUEST_STATUS_DONE = 8

CHOICES_REQUEST_STATUS = (
    (REQUEST_STATUS_REQUEST, '询价中'),
    (REQUEST_STATUS_QUOTE, '报价中'),
    (REQUEST_STATUS_CANCEL, '取消'),
    (REQUEST_STATUS_DONE, '完成结束')
)
