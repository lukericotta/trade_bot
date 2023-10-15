#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 10:49:09 2023

@author: lucianoricotta
"""

import alpaca_trade_api as tradeapi
from alpaca.trading.client import TradingClient

# Set your Alpaca API key and secret
API_KEY = 'PKF0FX6DX5ST3PQ4J0CS'
API_SECRET = '7Syxy7eeQXPwe7tGdZ659HCVLf8rSUNzwj5UIYxa'
BASE_URL = 'https://paper-api.alpaca.markets'  # For paper trading

ORDERS_URL = '{}/v2/orders'.format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID':API_KEY,'APCA-API-SECRET-KEY':API_SECRET}

api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

trading_client = TradingClient(API_KEY, API_SECRET)