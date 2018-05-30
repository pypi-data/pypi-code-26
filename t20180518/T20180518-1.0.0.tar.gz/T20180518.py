# for each_item in movies:
#     if isinstance(each_item,list):
#         for nested_item in each_item:
#             if isinstance(nested_item,list):
#                 for super_item in nested_item:
#                     print(super_item)
#             else:
#                 print(nested_item)
#     else:
#         print(each_item)

def print_lol(the_list,level):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='mm')
            print(each_item)