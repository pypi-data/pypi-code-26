import asyncio
import aiohttp
from bs4 import BeautifulSoup, SoupStrainer

base_url = 'http://gall.dcinside.com/board/view/?id=cat&no='
header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'}

strainer = SoupStrainer('div', attrs={'class': [
    're_gall_top_1',    # 제목, 글쓴이, 작성시각
    'btn_recommend',    # 추천, 비추천
    'gallery_re_title', # 댓글
    's_write',          # 본문
]})


def parse_post(markup, parser, strainer):
    soup = BeautifulSoup(markup, parser, parse_only=strainer)

    if not str(soup):
        soup = BeautifulSoup(markup, parser)

        if '/error/deleted/' in str(soup):
            return None
        elif '해당 갤러리는 존재하지 않습니다' in str(soup):
            raise Exception
        else:
            pass

    # temp_info = soup.find(attrs={'class': 'w_top_right'})
    # timestamp = temp_info.find('b').getText()

    # user_info = soup.find(attrs={'class': 'user_layer'})
    # user_id = user_info['user_id']
    # user_ip = '' if user_id else temp_info.find(attrs={'class': 'li_ip'}).string
    # nickname = user_info['user_name']

    # title = soup.find('dl', attrs={'class': 'wt_subject'}).find('dd').getText()
    # view_cnt = int(soup.find('dd', attrs={'class': 'dd_num'}).string)
    # view_up = int(soup.find(id='recommend_view_up').string)
    # view_dn = int(soup.find(id='recommend_view_down').string)
    # comment_cnt = int(soup.find(id='re_count').string)
    body = soup.find('div', attrs={'class': 's_write'}).find('td').getText()

    # post = {
    #     'user_id': user_id,
    #     'user_ip': user_ip,
    #     'nickname': nickname,

    #     'title': title,
    #     'written_at': timestamp,

    #     'view_up': view_up,
    #     'view_dn': view_dn,
    #     'view_cnt': view_cnt,
    #     'comment_cnt': comment_cnt,
    #     'body': body,
    # }

    return body

idx = 0

async def download(i: int):
    connector = aiohttp.TCPConnector(limit=16)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(base_url+str(i), headers=header) as res:
            with open(f'data/dcinside.txt', 'a+', encoding='utf-8') as f:
                response = await res.text()
                soup = BeautifulSoup(response, 'lxml', parse_only=strainer)
                try:
                    title = soup.find('dl', attrs={'class': 'wt_subject'}).find('dd').getText()
                    temp_info = soup.find(attrs={'class': 'w_top_right'})
                    timestamp = temp_info.find('b').getText()
                    body = soup.find('div', attrs={'class': 's_write'}).find('td').getText()
                    f.write("@title: %s" % title)
                    f.write("@timestamp: %s" % timestamp)
                    f.write("@content:%s" % body)
                except AttributeError:
                    pass
                global idx
                idx += 1
                print(idx)

import time
start_ = time.time()
tasks = [download(x) for x in range(0, 10000)]
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(asyncio.wait(tasks))
except ValueError:
    loop.close()
print("async 총걸린시간 {}".format(time.time() - start_)) # 약 1~2초 환경에따라 다름