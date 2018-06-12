# -*- coding: utf-8 -*-

"""
apollo python client
使用说明: http://wiki.intra.yongqianbao.com/pages/viewpage.action?pageId=11928499
author: sunguangran@daixiaomi.com
"""

import json
import sys
import threading
import time

import requests
from django.conf import settings

from pynavi.common import get_local_ip


class ApolloClient(object):
    """
    apollo python client
    """

    _DEFAULT_CONFIG_SERVER_ADDR = 'http://192.168.1.255:8080' if settings.DEBUG else ''

    def __init__(self, app_id, config_server=None, cluster='default', timeout=90, local_ip=None):
        self.config_server = config_server if config_server else self._DEFAULT_CONFIG_SERVER_ADDR
        self.appId = app_id
        self.cluster = cluster
        self.timeout = timeout
        self.stopped = False
        self._stopping = False
        self.ip = local_ip if local_ip else get_local_ip()

        self._notification_map = {'application': -1}

        # 本地缓存
        self._cache = {}

    def _listener(self):
        while not self._stopping:
            self._long_poll()

        self.stopped = True

    def start(self):
        """
        start the long polling daemon thread
        :return:
        """
        if not self._cache:
            self._long_poll()

        t1 = threading.Thread(target=self._listener, args=())
        t1.setDaemon(True)
        t1.start()

        return self

    def stop(self):
        self._stopping = True

    def _http_get_cached(self, k, default_val, namespace='application'):
        """
        该接口会从缓存中获取配置，适合频率较高的配置拉取请求，如简单的每30秒轮询一次配置
        :param k:
        :param default_val:
        :param namespace:
        :return:
        """
        url = '{}/configfiles/json/{}/{}/{}?ip={}'.format(self.config_server, self.appId, self.cluster, namespace, self.ip)
        resp = requests.get(url)
        if resp.ok:
            data = resp.json()
            self._cache[namespace] = data
        else:
            data = self._cache[namespace]

        return data[k] if k in data else default_val

    def _http_get_ignore_cache(self, namespace='application'):
        """
        该接口会直接从数据库中获取配置，可以配合配置推送通知实现实时更新配置
        :param namespace:
        :return:
        """
        url = '{}/configs/{}/{}/{}?ip={}'.format(self.config_server, self.appId, self.cluster, namespace, self.ip)
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            self._cache[namespace] = data['configurations']

    def _long_poll(self):
        url = '{}/notifications/v2'.format(self.config_server)
        notifications = []
        for k in self._notification_map:
            notification_id = self._notification_map[k]
            notifications.append({
                'namespaceName' : k,
                'notificationId': notification_id
            })

        resp = requests.get(url=url, params={
            'appId'        : self.appId,
            'cluster'      : self.cluster,
            'notifications': json.dumps(notifications, ensure_ascii=False)
        }, timeout=self.timeout)

        # 配置无变化
        if resp.status_code == 304:
            return

        if resp.status_code == 200:
            data = resp.json()
            for entry in data:
                ns = entry['namespaceName']
                nid = entry['notificationId']
                self._http_get_ignore_cache(ns)
                self._notification_map[ns] = nid
        else:
            time.sleep(self.timeout)

    def get_value(self, k, default_val=None, namespace='application', auto_fetch=False):
        if namespace not in self._notification_map:
            self._notification_map[namespace] = -1

        if namespace not in self._cache:
            self._cache[namespace] = {}
            self._long_poll()

        if k in self._cache[namespace]:
            return self._cache[namespace][k]

        if auto_fetch:
            return self._http_get_cached(k, default_val, namespace)

        return default_val


if __name__ == '__main__':
    # test
    client = ApolloClient(app_id=1001).start()
    while True:
        if sys.version_info[0] < 3:
            key = raw_input('Press any key to quit...')
        else:
            key = input('Press any key to quit...')

        if key.lower() == 'quit':
            break

        print(client.get_value(k=key, default_val='none'))

    client.stop()
