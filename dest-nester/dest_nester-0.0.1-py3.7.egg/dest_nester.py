'''
demo_nester.py模块,提供:
    1.print_lol函数,作用:打印列表(可处理嵌套列表)    
'''
#1
'''
    参数:
                    the_list:要打印的列表(可包含嵌套列表)
                    each_item:列表元素
      实现:
                    所指定的列表中的每个数据项会(递归地)输出到屏幕上,各数据各占一行
    '''
def print_lol(the_list):   
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
