import random
import getip
def readip():
    try:
        getip.get_ip()
    except:
        pass
    f = open('ip.txt', 'r')
    text = f.read()
    f.close()
    ip = text.split()
    id = []
    for i in range(0,100):
        id.append(i)
    # print(len(ip),len(id))
    ip_list = []
    for i in range(0,100):
        ip_list.append([id[i],ip[i]])

    # print(proxies)

    num = random.randint(0,99)
    # print(num)
    ip = ['http',ip_list[num][1]]
    # print(ip)
    proxies = dict((ip,))
    # print(proxies)
    return proxies