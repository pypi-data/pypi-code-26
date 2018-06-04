from select import select
from functools import partial

wait = partial(select, [], [], [])