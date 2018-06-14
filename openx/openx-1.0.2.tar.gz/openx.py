#coding=utf-8
"""处理list列表中的嵌套问题，True控制是否启用，默认不缩进，缩进是由level进行控制"""
def open_x(the_list,indent=False,level=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            open_x(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end="")
            print(each_item)
				
				