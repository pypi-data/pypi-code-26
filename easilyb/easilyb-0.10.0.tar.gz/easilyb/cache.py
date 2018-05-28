import time
import logging
import json
from threading import Lock
logger = logging.getLogger(__name__)
TTL = 3600
DEFAULT_NAMESPACE = "DEFAULT_NAMESPACE"
DEFAULT_CLEAN_INTERVAL = 60


class SimpleCache:
    def __init__(self, clean_interval=DEFAULT_CLEAN_INTERVAL):
        self._db = dict()
        self.clean_interval = clean_interval
        self._last_clean = time.time()
        self._lock = Lock()

    def get(self, key, action=None, action_kwargs=None, namespace=DEFAULT_NAMESPACE,
            expires=True, ttl=TTL):
        with self._lock:
            self._auto_clean()
            if namespace not in self._db:
                self._db[namespace] = dict()
            if key in self._db[namespace] and not self._db[namespace][key].expired():
                return self._db[namespace][key].value
            elif action is not None:
                action_kwargs = action_kwargs or dict()
                ret = action(**action_kwargs)
                entry = CacheEntry(key, ret, expires=expires, ttl=ttl, action=action, action_kwargs=action_kwargs)
                self._db[namespace][key] = entry
                return self._db[namespace][key].value
            else:
                raise NotFoundInCache()

    def put(self, key, value, action=None, action_kwargs=None, namespace=DEFAULT_NAMESPACE,
            expires=True, ttl=TTL):
        with self._lock:
            self._auto_clean()
            if namespace not in self._db:
                self._db[namespace] = dict()
            entry = CacheEntry(key, value, expires=expires, ttl=ttl, action=action, action_kwargs=action_kwargs)
            self._db[namespace][key] = entry

    def cached(self, func=None, expires=True, ttl=TTL, namespace=DEFAULT_NAMESPACE):
        def decorator(func):
            def wrapper(*a, **ka):
                namespace_ = namespace + "." + func.__name__
                key = _get_key(a, ka)
                try:
                    return self.get(key, namespace=namespace_)
                except NotFoundInCache:
                    value = func(*a, **ka)
                    self.put(key, value, expires=expires, ttl=ttl, namespace=namespace_)
                    return value
            return wrapper

        if callable(func):
            return decorator(func)
        else:
            return decorator

    def get_namespace_cache(self, namespace):
        return NamespaceCache(self, namespace)

    def _auto_clean(self):
        if time.time() - self._last_clean > self.clean_interval:
            self.clean()

    def clean(self):
        for sp in self._db:
            to_remove = list()
            for k,v in self._db[sp].items():
                if v.expired():
                    to_remove.append(k)
            for k in to_remove:
                del self._db[sp][k]
        self._last_clean = time.time()


class NamespaceCache:
    def __init__(self, maincache, namespace):
        self.namespace = namespace
        self.cache = maincache

    def get(self, key, action=None, action_kwargs=None, expires=True, ttl=TTL):
        return self.cache.get(key, action=action, action_kwargs=action_kwargs, expires=expires, ttl=ttl,
                       namespace=self.namespace)

    def put(self, key, value, action=None, action_kwargs=None, expires=True, ttl=TTL):
        self.cache.put(key, value, action=action, action_kwargs=action_kwargs, expires=expires, ttl=ttl,
                       namespace=self.namespace)

    def cached(self, func=None, expires=True, ttl=TTL):
        return self.cache.cached(func, expires, ttl, namespace=self.namespace)


class NotFoundInCache(Exception):
    pass


class CacheEntry:
    def __init__(self, key, value, expires=True, ttl=TTL, action=None, action_kwargs=None):
        self.key = key
        self.value = value
        self.expires = expires
        self.ttl = ttl
        self.creation_time = time.time()
        self.expire_time = self.creation_time + ttl
        self.action = action
        self.action_kwargs = action_kwargs

    def expired(self):
        return self.expires and time.time() > self.expire_time


class _KeyEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except:
            return str(obj)


def _get_key(args, kwargs):
    return json.dumps({'args':args, 'kwargs': kwargs}, sort_keys=True, cls=_KeyEncoder)


