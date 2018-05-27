from datetime import datetime
from functools import partial
from uuid import UUID

import simplejson


def encoder(obj):
    if isinstance(obj, UUID):
        return obj.hex
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError


loads = partial(simplejson.loads, use_decimal=True)
dumps = partial(simplejson.dumps,
                use_decimal=True,
                default=encoder,
                iterable_as_array=True
                )

__all__ = ['loads', 'dumps']
