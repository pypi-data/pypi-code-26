def process(s):
    """
process(string) -> A list containing processed tabulation
```
>>> process('''
for i in a:
    print('i')
    if i == '':
        break
''')
['for i in a:', ["print('i')", "if i == '':", ['break']]]

    """
    d = []
    ds = '['
    ct = 0
    ft = ''
    allPlain = True
    for k in s.splitlines():
        if k.startswith(' '):
            allPlain = False
    if allPlain:
         return s.splitlines()
    for j in s.splitlines():
        lineChosen = False
        while j.startswith(' '):
            ft+=' '
            j = j[1:]
            lineChosen = True
        if lineChosen:
            break
    for i in s.splitlines():
        
        ni = i
        t = 0
        while True:
            if ni.startswith(ft):
                ni = ni[len(ft):]
                t+=1
            else:
                hasToPutComma = False
                pt = t
                while t<ct:
                    ds+= ']'
                    t+=1
                    hasToPutComma = True
                while t>ct:
                    ds += '['
                    t-=1
                if hasToPutComma:
                    ds+=','
                ct =pt
                ds+="'"
                ds+=ni.replace('"','\\"').replace("'","\\'")
                ds+="'"
                ds+=','
                '''while t!=0:
                    ni = [ni]
                    t-=1'''
                #d.append(ni)
                break
    while pt>0:
        ds+=']'
        pt-=1
    return eval(ds+']')

from sys import argv
if __name__ == '__main__':
    ##print(process(argv[1]))
    with open(argv[1]) as f:
        print(process(
            f.read()
        ))