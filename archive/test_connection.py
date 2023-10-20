#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 10:48:51 2023

@author: lucianoricotta
"""

from apisetup import *

# obtain account information
account = api.get_account()
print(account.buying_power)