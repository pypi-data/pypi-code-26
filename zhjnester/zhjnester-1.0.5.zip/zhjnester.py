"""
这是一个演示嵌套方法的示例程序，能打印出list类型的数据单元内容
"""
__author__ = 'hjzheng'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打印出list类型的数据单元内容
"""
def print_lol(the_list,level=0):
   for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t"),
            print(each_item)

"""
import zhjnester
movies=['红高粱',1975,'张艺谋',91,['姜文',['太阳照常升起','让子弹飞','红河谷']]]
zhjnester.print_lol(movies,4)
"""