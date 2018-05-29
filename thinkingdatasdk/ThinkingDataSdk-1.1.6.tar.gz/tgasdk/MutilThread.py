import random
import threading

import time

from tgasdk import TGAnalytics, LoggingConsumer, datetime

tga = TGAnalytics(LoggingConsumer("F:/home/sdk/log"))

properties = {
    #"#time":'2018-01-12 20:46:56',
    "custome":datetime.datetime.now(),
    "#ip":"192.168.1.1",
    "Product_Name":"a",
    '#os':'windows',
    "today":datetime.date.today()

}



def thread_run(urls):
    print('Current %s is running...' % threading.current_thread().getName())
    for url in range(10000):
        print('%s ------>> %s' % (threading.current_thread().name, url))
        tga.track('dis', None, threading.current_thread().name, properties)
    print('%s ended' % threading.current_thread().name)


if __name__ == '__main__':
    print('%s is running......' % threading.current_thread().name)
    print(threading.current_thread().getName())
    print()
    t1 = threading.Thread(target=thread_run, name='Thread_1', args=(['url_1', 'url_2', 'url_3'],))
    t2 = threading.Thread(target=thread_run, name='Thread_2', args=(['url_4', 'url_5', 'url_6'],))
    t3 = threading.Thread(target=thread_run, name='quanjie', args=(['url_4', 'url_5', 'url_6'],))

    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    tga.close()



