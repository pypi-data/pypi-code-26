def plist(iterable, ncols=3, whitespace=20):

    for i, x in enumerate(iterable):
        if i%ncols == 0 and i > 0:
            print()
            
        print(str(x).ljust(whitespace,' '), end='')
