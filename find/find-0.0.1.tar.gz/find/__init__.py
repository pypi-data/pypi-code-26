#!/usr/bin/env python
import os
from public import public


@public
def find(path, followlinks=False):
    # followlinks
    if not os.path.exists(path):
        return
    for root, dirs, files in os.walk(path, followlinks=followlinks):
        for file in files:
            yield os.path.join(root, file)
