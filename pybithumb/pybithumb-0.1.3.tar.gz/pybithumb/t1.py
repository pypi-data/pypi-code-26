

test = {"data":{'abc':1}}
test = []
try:
    print(test['data']['abc'])
except Exception as e:
    print("Error" + str(e))
    print("get_market_detail", e.__class__.__name__)