import requests


headers = {'pragma': 'no-cache',
           'cache-control': 'no-cache',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'x-client-data': 'CI62yQEIprbJAQjEtskBCKmdygEI153KAQioo8oB',
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7'
           }

response = requests.get('https://www.google.com/', headers=headers)
print(response.text)
