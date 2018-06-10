import os
import pathlib
import wget
import requests
import threading
from bs4 import BeautifulSoup


def download(m, i, loc):
    os.system('cd ' + loc)
    for i in range(0, len(m)):
        file = ("https:" + m[i]['href'])
        # cm = str(('wget -c -nc -t 3 ') + file)
        # print('cm : ', cm)
        # os.system(cm)
        wget.download(file, str(loc))
        # print('got : ', file)


def runner(media, chunkSize, nThreads, loc):
    threads = []
    mediaChunks = chunks(media, chunkSize)
    mediaChunks = list(mediaChunks)
    leftovers = len(media) - (chunkSize * nThreads)
    if leftovers != 0:
        nThreadsS = nThreads + 1
    else:
        nThreadsS = nThreads
    for i in range(nThreadsS):
        if i != nThreadsS - 1:
            t = threading.Thread(target=download, args=(mediaChunks[i], i, loc,))
        else:
            t = threading.Thread(target=download, args=(media[-leftovers:], i, loc,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def load(url):
    try:
        page = requests.get(str(url))
        soup = BeautifulSoup(page.content, "html.parser")
        media = soup.find_all("a", class_="fileThumb", href=True)
    except Exception:
        print("\n Aborted due to an error.\n")
        exit()
    return list(media)


def fc(url, board, threadNumber, nThreads):
    loc = (str(pathlib.Path.home()) + '/FoChan/' + board + '/' + threadNumber)
    if not os.path.exists(loc):
        os.makedirs(loc, mode=0o777)
    media = load(url)
    print('\n< downloading to: ', loc, ' | threads: ', nThreads, ' | mediaSize: ', len(media), ' >\n')
    rawChunkSize = len(media) / nThreads
    runner(media, int(rawChunkSize), int(nThreads), str(loc))
