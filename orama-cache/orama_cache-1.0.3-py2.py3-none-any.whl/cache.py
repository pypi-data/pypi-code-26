# -*- coding: utf-8 -*-
from memcache import Client
from .memcached_stats import MemcachedStats
from .constants import DEFAULT_CACHE_PORT, DEFAULT_CACHE_KEY_PREFIX,\
    MAXIMUM_CACHE_TIMEOUT, DEFAULT_INSTANCE_NAME, LOCK_EXPIRE


class CacheManagerService:
    _cache_manager_instance = None
    _instances = {}
    _cache_instance = None

    def __init__(self, cache_instance_name=None, *args, **kwargs):
        self._cache_instance = self._instances.get(cache_instance_name or DEFAULT_INSTANCE_NAME)

    def __new__(cls, cache_instance_name=None, *args, **kwargs):
        if cls._cache_manager_instance is not None:
            return cls._cache_manager_instance
        else:
            instance = cls._cache_manager_instance = super(CacheManagerService, cls).__new__(cls, *args, **kwargs)
            return instance

    def setup_cache_instance(self, cache_instance_name, cache_instance_ip, cache_instance_port=None):
        cache_port = str(cache_instance_port) or DEFAULT_CACHE_PORT
        server = "{cache_instance_ip}:{cache_port}".format(cache_instance_ip=cache_instance_ip, cache_port=cache_port)
        self._instances[cache_instance_name] = Client([server])

    def _get_timeout(self, timeout):
        if isinstance(timeout, int):
            return timeout if timeout <= MAXIMUM_CACHE_TIMEOUT else MAXIMUM_CACHE_TIMEOUT
        return timeout

    def _get_cache_keys(self):
        (host, port) = self._cache_instance.servers[0].address
        cache = MemcachedStats(host, port)
        return [key[3:] if key[:3] == ':1:' else key for key in cache.keys()]

    def clear_cache_keys_from_prefix(self, cache_prefix, cache_instance=None):
        for cache_key in self._get_cache_keys(cache_instance=cache_instance):
            if cache_key[:len(cache_prefix)] == cache_prefix:
                return self.delete(cache_key, cache_instance=cache_instance)

    def clear_cache_keys_from_list(self, CACHE_KEYS_LIST):
        CACHE_KEYS_LIST = DEFAULT_CACHE_KEY_PREFIX + str(CACHE_KEYS_LIST)
        cache_keys = self._cache_instance.get(CACHE_KEYS_LIST)
        if cache_keys:
            for cache_key in cache_keys:
                if not str(cache_key).startswith(DEFAULT_CACHE_KEY_PREFIX):
                    cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
                self._cache_instance.delete(cache_key)
            self._cache_instance.delete(CACHE_KEYS_LIST)

    def clear_cache_keys_from_list_of_keys_list(self, CACHE_KEYS_LIST):
        CACHE_KEYS_LIST = DEFAULT_CACHE_KEY_PREFIX + str(CACHE_KEYS_LIST)
        cache_keys = self._cache_instance.get(CACHE_KEYS_LIST)
        if cache_keys:
            for cache_key in cache_keys:
                self.clear_cache_keys_from_list(cache_key)
            self._cache_instance.delete(CACHE_KEYS_LIST)

    def compare_and_set(self, cache_key, cache_value, timeout, parent_cache_key=None):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        if parent_cache_key is not None:
            parent_cache_key = DEFAULT_CACHE_KEY_PREFIX + str(parent_cache_key)
        timeout = self._get_timeout(timeout)
        result = self._cache_instance.cas(cache_key, cache_value, timeout)
        if parent_cache_key and result:
            parent_cache_key_list = self._cache_instance.get(parent_cache_key)
            if parent_cache_key_list and cache_key not in parent_cache_key_list:
                parent_cache_key_list.append(cache_key)
            elif parent_cache_key_list is None:
                parent_cache_key_list = [cache_key]
            self._cache_instance.set(parent_cache_key, parent_cache_key_list, timeout)
        return result

    def add(self, cache_key, timeout=None):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        timeout = self._get_timeout(timeout) if timeout else LOCK_EXPIRE
        return self._cache_instance.add(cache_key, True, timeout)

    def append(self, cache_key, cache_value, timeout):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        timeout = self._get_timeout(timeout)
        return self._cache_instance.append(cache_key, cache_value, timeout)

    def prepend(self, cache_key, cache_value, timeout):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        timeout = self._get_timeout(timeout)
        return self._cache_instance.prepend(cache_key, cache_value, timeout)

    def delete(self, cache_key, parent_cache_key=None, timeout=None):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        if parent_cache_key is not None:
            parent_cache_key = DEFAULT_CACHE_KEY_PREFIX + str(parent_cache_key)
        result = self._cache_instance.delete(cache_key)
        if parent_cache_key:
            parent_cache_key_list = self._cache_instance.get(parent_cache_key)
            if parent_cache_key_list:
                if cache_key in parent_cache_key_list:
                    parent_cache_key_list.remove(cache_key)
                    self._cache_instance.set(parent_cache_key, parent_cache_key_list, timeout)
        return result

    def delete_multiple(self, cache_keys, parent_cache_key=None, timeout=None):
        cache_keys = [str(cache_key) for cache_key in cache_keys]
        if parent_cache_key is not None:
            parent_cache_key = DEFAULT_CACHE_KEY_PREFIX + str(parent_cache_key)
        self._cache_instance.delete_multi(cache_key, key_prefix=DEFAULT_CACHE_KEY_PREFIX)
        if parent_cache_key:
            parent_cache_key_list = self._cache_instance.get(parent_cache_key)
            if parent_cache_key_list:
                for cache_key in cache_keys:
                    if cache_key in parent_cache_key_list:
                        parent_cache_key_list.remove(cache_key)
                self._cache_instance.set(parent_cache_key, parent_cache_key_list, timeout)

    def flush_all(self):
        self._cache_instance.flush_all()

    def flush_all_caches(self):
        for cache_instance_name in self._instances:
            self.flush_all(cache_instance=cache_instance_name)

    def get(self, cache_key):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        return self._cache_instance.get(cache_key)

    def get_multiple(self, cache_keys):
        cache_keys = [str(cache_key) for cache_key in cache_keys]
        return self._cache_instance.get_multi(cache_keys, key_prefix=DEFAULT_CACHE_KEY_PREFIX)

    def get_to_compare(self, cache_key):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        return self._cache_instance.gets(cache_key)

    def increment(self, cache_key, delta=1):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        self._cache_instance.incr(cache_key, delta)

    def decrement(self, cache_key, delta=1):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        self._cache_instance.decr(cache_key, delta)

    def update_timeout(self, cache_key, timeout, parent_cache_key=None):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        timeout = self._get_timeout(timeout)
        self._cache_instance.touch(cache_key, timeout, noreply=True)
        if parent_cache_key:
            self._cache_instance.touch(parent_cache_key, timeout, noreply=True)

    def set(self, cache_key, cache_value, timeout=None, parent_cache_key=None):
        cache_key = DEFAULT_CACHE_KEY_PREFIX + str(cache_key)
        if parent_cache_key is not None:
            parent_cache_key = DEFAULT_CACHE_KEY_PREFIX + str(parent_cache_key)
        timeout = self._get_timeout(timeout)
        result = self._cache_instance.set(cache_key, cache_value, timeout)
        if parent_cache_key:
            parent_cache_key_list = self._cache_instance.get(parent_cache_key)
            if parent_cache_key_list and cache_key not in parent_cache_key_list:
                parent_cache_key_list.append(cache_key)
            elif parent_cache_key_list is None:
                parent_cache_key_list = [cache_key]
            self._cache_instance.set(parent_cache_key, parent_cache_key_list, timeout)
        return result

    def set_multiple(self, mapping, timeout=None, parent_cache_key=None):
        for cache_key in mapping:
            cache_value = mapping[cache_key]
            mapping.pop(cache_key, None)
            mapping[str(cache_key)] = cache_value
        if parent_cache_key is not None:
            parent_cache_key = DEFAULT_CACHE_KEY_PREFIX + str(parent_cache_key)
        timeout = self._get_timeout(timeout)
        self._cache_instance.set_multi(mapping, timeout, key_prefix=DEFAULT_CACHE_KEY_PREFIX)
        if parent_cache_key:
            parent_cache_key_list = self._cache_instance.get(parent_cache_key)
            if parent_cache_key_list:
                for cache_key in mapping:
                    if cache_key not in parent_cache_key_list:
                        parent_cache_key_list.append(cache_key)
            else:
                parent_cache_key_list = list(mapping.keys())
            self._cache_instance.set(parent_cache_key, parent_cache_key_list, timeout)
