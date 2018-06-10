from .fc import fc
import sys
import re


def main():
    if len(sys.argv) == 1:
        print("\nUsage: fochan <NUMBER_OF_THREADS> <URL>\n")
        exit()
    else:
        nThreads = sys.argv[1]
        url = sys.argv[2]

        bb = re.search('4chan.org/(.*?)/thread', str(url))
        if bb:
            board = bb.group(1)

        tn = re.findall('/thread/(.+)', str(url))
        threadNumber = str(tn[0])

        # print(url)
        # print(board)
        # print(threadNumber)
        # print(nThreads)

    fc(str(url), str(board), str(threadNumber), int(nThreads))
