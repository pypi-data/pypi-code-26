def budget(money):
    beer = money // 2
    bottle, top = beer, beer
    print("Can buy : ", beer)
    while True:
        a, b = bottle // 2, top // 4
        tmp = a + b
        if tmp >= 0:
            beer += a + b
            bottle = a + b + bottle % 2
            top = a + b + top % 4
            print("Beer={}, Bottle ={}, Top={}".format(beer, bottle, top))
            if not bottle // 2 + top // 4:
                break
    return print("Final drink = {}".format(beer))
