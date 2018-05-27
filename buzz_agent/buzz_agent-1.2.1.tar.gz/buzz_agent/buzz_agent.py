# -*- coding: utf-8 -*-

import logging.config
import json
import time
import logging
import os.path
import hashlib
import numbers
import requests
import whisper
from .six import _thread, urljoin

logger = logging.getLogger('buzz_agent')


LOAD_CONFIG_PATH = '/config'
ALARM_PATH = '/alarm'


class BuzzAgent(object):

    path = None
    domain = None
    timeout = None
    secret = None
    interval = None

    last_run_time = None
    # 默认上一个值是0
    last_value_dict = None
    alarm_config = None

    def __init__(self, config):
        """
        :param config:
            STAT_PATH: 统计文件路径
            DOMAIN: 域名
            TIMEOUT: 拉取config超时
            SECRET: 密钥
            INTERVAL: 隔多久检查一次。无需太短，whisper整理数据有最小时长，太短获取的都是None
        :return:
        """
        if hasattr(config, 'LOGGING'):
            logging.config.dictConfig(config.LOGGING)

        self.stat_path = config.STAT_PATH
        self.domain = config.DOMAIN
        self.timeout = config.TIMEOUT
        self.secret = config.SECRET
        self.interval = config.INTERVAL

        self.last_value_dict = dict()

    def run(self):
        while True:
            try:
                self.process()
            except KeyboardInterrupt:
                break
            except:
                logger.error('exc occur.', exc_info=True)

            time.sleep(self.interval)

    def process(self):
        if not self._load_config():
            if not self.alarm_config:
                # 只有没有配置的情况下才报错
                return False

        now = time.time()
        if not self.last_run_time:
            self.last_run_time = now - self.interval

        for conf in self.alarm_config:
            stat_name = conf['stat_name']

            stat_path = os.path.join(self.stat_path, stat_name.replace('.', '/')) + '.wsp'
            logger.debug('stat_path: %s', stat_path)

            last_value = self.last_value_dict.get(stat_name, 0)

            try:
                values = [last_value] + self._fetch_stat_data(stat_path, self.last_run_time, now)
            except:
                logger.error('exc occur. stat_path: %s, conf: %s', stat_path, conf, exc_info=True)
                continue

            for k, v in enumerate(values):
                if k < 1:
                    # 从第二个开始
                    continue

                # 告警的配置项有几个
                alarm_benchmark = 0
                # 被触发的配置项有几个
                alarm_num = 0

                # 命中的，即有效的
                hit_number_value = None
                hit_slope_value = None
                hit_delta_value = None

                if conf['number_cmp'] is not None and conf['number_value'] is not None:
                    # 值

                    alarm_benchmark += 1

                    number_value = v
                    if self._is_right(number_value, conf['number_cmp'], conf['number_value']):
                        alarm_num += 1

                        # 命中才给值
                        hit_number_value = number_value

                if conf['slope_cmp'] is not None and conf['slope_value'] is not None:
                    # 斜率

                    alarm_benchmark += 1

                    # 说明可以计算斜率
                    pre_val = values[k-1]

                    # pre_val 不可以为None、0
                    # v 不可以为None
                    if pre_val and v is not None:
                        slope_value = 1.0 * (v - pre_val) / pre_val
                    else:
                        slope_value = None

                    # logger.debug('slope_value: %s, pre_val: %s, v: %s', slope_value, pre_val, v)

                    if self._is_right(slope_value, conf['slope_cmp'], conf['slope_value']):
                        alarm_num += 1

                        # 命中才给值
                        hit_slope_value = slope_value

                if conf['delta_cmp'] is not None and conf['delta_value'] is not None:
                    # 差值

                    alarm_benchmark += 1

                    # 说明可以计算差值
                    pre_val = values[k-1]

                    # pre_val 不可以为None
                    # v 不可以为None
                    if pre_val is not None and v is not None:
                        delta_value = v - pre_val
                    else:
                        delta_value = None

                    # logger.debug('delta_value: %s, pre_val: %s, v: %s', delta_value, pre_val, v)

                    if self._is_right(delta_value, conf['delta_cmp'], conf['delta_value']):
                        alarm_num += 1

                        # 命中才给值
                        hit_delta_value = delta_value

                # logger.debug('v: %s, alarm_benchmar: %s, alarm_num: %s', v, alarm_benchmark, alarm_num)
                if alarm_benchmark and alarm_benchmark == alarm_num:
                    # 说明要告警

                    # self._alarm(conf['id'], hit_number_value, hit_slope_value)
                    _thread.start_new_thread(
                        self._alarm,
                        (conf['id'], hit_number_value, hit_slope_value, hit_delta_value)
                    )
                    # 每个stat告警完，就赶紧换下一个
                    break

            if values:
                self.last_value_dict[stat_name] = values[-1]

        # 避免重复告警
        self.last_run_time = now

    def _is_right(self, left, op, right):
        """
        判断是否是符合的
        :param left:
        :param op:
        :param right:
        :return:
        """
        if left is not None:
            assert \
                op in ('<', '<=', '>', '>=', '==', '!=') and \
                isinstance(left, numbers.Number) and \
                isinstance(right, numbers.Number)

            code = '%s %s %s' % (left, op, right)

            return eval(code)
        else:
            return False

    def _fetch_stat_data(self, stat_path, from_time, to_time):
        """
        获取数据
        :return:
        """
        # return [10, 100, 100]
        time_info, values = whisper.fetch(stat_path, from_time, to_time)

        return values

    def _load_config(self):
        """
        读取配置
        :return:
        """

        url = urljoin('http://' + self.domain, LOAD_CONFIG_PATH)

        rsp = requests.get(url)
        if not rsp.ok:
            logger.error('fail. url: %s, code: %s', url, rsp.status_code)
            return False

        self.alarm_config = rsp.json()['config']

        return True

    def _alarm(self, config_id, number_value=None, slope_value=None, delta_value=None):
        """
        告警
        """
        logger.info('config_id: %s, number_value: %s, slope_value: %s, delta_value: %s',
                    config_id, number_value, slope_value, delta_value)

        url = urljoin('http://' + self.domain, ALARM_PATH)

        data = json.dumps(dict(
            config_id=config_id,
            number_value=number_value,
            slope_value=slope_value,
            delta_value=delta_value,
        ))

        sign = hashlib.md5('|'.join((self.secret, data))).hexdigest()

        rsp = requests.post(url, dict(
            data=data,
            sign=sign,
        ), timeout=self.timeout)

        if not rsp.ok:
            logger.error('status fail. url: %s, data: %s, sign: %s, code: %s',
                         url, data, sign, rsp.status_code)
            return False

        if rsp.json()['ret'] != 0:
            logger.error('content invalid. url: %s, data: %s, sign: %s, content: %s',
                         url, data, sign, rsp.json())
            return False

        return True
