import json

funds = []

with open("contracts.json",'r') as f:
    for line in f:
        line = json.loads(line.replace("'",'"'))
        if line['balance'] != "0 Ether":
            funds.append(line)
            print(line)

newlist = sorted(funds, key=lambda k:float(k['balance'].split(" ",1)[0].replace(",","")) if k['balance']!='-' else 0)
for i in newlist:
    print (i)