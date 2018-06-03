def print_lol(the_list):
    print('this is print_lol:')
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)