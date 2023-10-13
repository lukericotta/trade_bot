#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 10:49:09 2023

@author: lucianoricotta
"""

import alpaca_trade_api as tradeapi

# Set your Alpaca API key and secret
API_KEY = 'PK2YL3D9EYZDFK7EYR25'
API_SECRET = 'RDZUKIJqpyZ1ITJgjH6vDsaIxZdhlgV38fPYzCuP'
BASE_URL = 'https://paper-api.alpaca.markets'  # For paper trading

ORDERS_URL = '{}/v2/orders'.format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID':API_KEY,'APCA-API-SECRET-KEY':API_SECRET}

api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')
