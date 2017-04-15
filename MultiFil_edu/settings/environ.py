#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import os

__author__ = 'Ziqin (Shaun) Rong'
__maintainer__ = 'Ziqin (Shaun) Rong'
__email__ = 'rongzq08@gmail.com'

FIREWORKS_LAUNCHPAD_FILE = "/path/to/your/fireworks/launchpad/file"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

print(REPO_ROOT)