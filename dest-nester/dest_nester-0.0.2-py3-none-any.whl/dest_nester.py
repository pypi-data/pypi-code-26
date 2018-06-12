'''
demo_nester.py模块,提供:
    1.print_lol函数,作用:打印列表(可处理嵌套列表)    
'''
#1
'''
    参数:
                    the_list:要打印的列表(可包含嵌套列表)
                    level:用来在遇到嵌套列表时需要插入的制表符数

      实现:
                    所指定的列表中的每个数据项会(递归地)输出到屏幕上,各数据各占一行,
                    遇到嵌套列表时会打印用户输入的数目的制表符数
'''
def print_lol(the_list,level):   
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for Tab in range(level):
                print("\t",end="")
            print(each_item)


