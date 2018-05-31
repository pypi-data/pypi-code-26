# coding: utf-8
import time
import redis

# time unit all is milliseconds
DEFAULT_RETRY_TIMES = 3
DEFAULT_RETRY_INTERVAL = 50
DEFAULT_EXPIRE = 30000


class RedLock:

    def __init__(self, rds, key, expire=DEFAULT_EXPIRE, retry_times=DEFAULT_RETRY_TIMES,
            retry_interval=DEFAULT_RETRY_INTERVAL):
        """
        Ref: https://redis.io/topics/distlock

        :param rds: redis connection(StrictRedis instance)
        :param key: lock key
        :param expire:  lock key expire ttl(ms)
        :param retry_times: retry times to get lock
        :param retry_interval: retry interval(ms)

        total max time is: retry_times * retry_interval(ms)
        """
        if not isinstance(rds, redis.StrictRedis):
            raise Exception('rds should be an instance of redis.StrictRedis')
        self.rds = rds
        self.key = key
        self.expire = expire
        self.retry_times = retry_times
        self.retry_interval = retry_interval
        self.value = time.time() * 1000 + self.expire  # ms

    def __enter__(self):
        return self.lock()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def release(self):
        if time.time() * 1000 < self.value:
            self.rds.delete(self.key)
        else:
            _value = self.rds.get(self.key)
            if _value == self.value:
                self.rds.delete(self.key)
            raise Exception('handle timeout after got redlock')

    def lock(self):
        for retry in range(self.retry_times + 1):
            if self.rds.set(self.key, self.value, px=self.expire, nx=True):
                return True
            time.sleep(self.retry_interval / 1000)

        return False

