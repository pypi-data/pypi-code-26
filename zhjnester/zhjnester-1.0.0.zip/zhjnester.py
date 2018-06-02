"""
这是一个演示嵌套方法的示例程序，能打印出list类型的数据单元内容
"""
__author__ = 'hjzheng'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打印出list类型的数据单元内容
"""
def print_lol(the_list):
   for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)

