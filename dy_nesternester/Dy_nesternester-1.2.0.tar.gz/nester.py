"""
movies=["The Grail",1975,"Terry Jones & Terry Gilliam",91,["Graham Chapman",
            ["Michael Palin","John Cleese","Terry Gilliam","Eric Idle",
                 "Terry Jones"]]]
"""
"""
for each_item in movies:
    if isinstance(each_item,list):
        for nested_item in each_item:
            if isinstance(nested_item,list):
                for nested_item_item in nested_item:
                    print(nested_item_item)
            else:
                print(nested_item)
    else:
        print(each_item)    
"""

def print_lol(listme,level):
    for each_item in listme:
        if isinstance(each_item,list):
            print_lol(each_item,level+1);
        else:
            for tab_stops in range(level):
                print("\t",end='')
            print(each_item)
            

