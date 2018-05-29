'''This is a pangyuwen_nester.py model,provide a function,named as print_lol(the_list),used to print list,which may very complex.'''

def print_lol(the_list):

    '''This is a funciton needs a input,the type is python list.
The use of this function is to print each itmes in the iuput list.'''
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
            print(each_item)
