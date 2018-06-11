from .models import Cache
from functools import wraps
import hashlib


def lrucache(key_str):
    def _lru_cache(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = key_str.format(*args, **kwargs)

            if len(key) > 100:
                key = hashlib.md5(key.encode('utf8')).hexdigest()

            type = '{}.{}'.format(func.__module__, func.__name__)

            try:
                return Cache.objects.get(
                    key=key,
                    type=type
                ).results
            except Cache.DoesNotExist:
                result = func(*args, **kwargs)

                Cache.objects.get_or_create(
                    key=key,
                    type=type,
                    defaults={
                        "results": result
                    }
                )
                return result

        return wrapper

    return _lru_cache
