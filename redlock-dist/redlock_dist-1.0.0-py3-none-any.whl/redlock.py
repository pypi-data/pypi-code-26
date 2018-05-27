# coding: utf-8
import time
import uuid
import redis

# time unit all is milliseconds
DEFAULT_RETRY_TIMES = 3
DEFAULT_RETRY_INTERVAL = 50
DEFAULT_EXPIRE = 30000
RELEASE_LUA_SCRIPT = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end
"""


class RedLock:

    def __init__(self, rds, key, value=None, expire=DEFAULT_EXPIRE, retry_times=DEFAULT_RETRY_TIMES,
                 retry_interval=DEFAULT_RETRY_INTERVAL):
        """
        Ref: https://redis.io/topics/distlock

        :param rds: redis connection(StrictRedis instance)
        :param key: lock key
        :param value: should be random and unique(default: uuid.uuid4().hex)
        :param expire:  lock key expire ttl(ms)
        :param retry_times: retry times to get lock
        :param retry_interval: retry interval(ms)

        total max time is: retry_times * retry_interval(ms)
        """
        if not isinstance(rds, redis.StrictRedis):
            raise Exception('rds should be an instance of redis.StrictRedis')
        self.rds = rds
        self.key = key
        self.value = value if value else uuid.uuid4().hex
        self.expire = expire
        self.retry_times = retry_times
        self.retry_interval = retry_interval

        self.rds._release_script = self.rds.register_script(RELEASE_LUA_SCRIPT)

    def __enter__(self):
        return self.lock()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def release(self):
        try:
            self.rds._release_script(keys=[self.key], args=[self.value])
        except Exception as e:
            print(e)

    def lock(self):
        for retry in range(self.retry_times + 1):
            if self.rds.set(self.key, self.value, px=self.expire, nx=True):
                return True
            time.sleep(self.retry_interval / 1000)

        return False

