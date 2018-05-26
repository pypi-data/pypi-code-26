# -*- coding: utf-8 -*-
#
# django-codenerix-vending
#
# Copyright 2017 Centrologic Computational Logistic Center S.L.
#
# Project URL : http://www.codenerix.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import uuid
import hashlib
import random
import string
from channels import Channel, Group

from django.db import models
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.conf import settings

from jsonfield import JSONField

from codenerix.models import CodenerixModel
