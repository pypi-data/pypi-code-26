#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: chanconfig/__init__.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 19.10.2017
from config import Config, ReadConfigurationError
from multiple_config import MultipleConfig


__all__ = ['Config', 'MultipleConfig', 'ReadConfigurationError']
__version__ = '0.0.4'
