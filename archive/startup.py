#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 10:10:03 2023

@author: lucianoricotta
"""

from apisetup import *
import alpaca_trade_api as tradeapi

def sell():
    # Submit a market order to buy 1 share of Apple at market price
    api.submit_order(
        symbol='AAPL',
        qty=.05,
        side='sell',
        type='market',
        time_in_force='day'
    )

def buy():
    # Submit a market order to buy 1 share of Apple at market price
    api.submit_order(
        symbol='AAPL',
        qty=1,
        side='buy',
        type='market',
        time_in_force='day'
    )

def stop_limit_buy():
    # Submit a market order to buy 1 share of Apple at market price
    api.submit_order(
        symbol='AAPL',
        qty=1,
        type='stop_limit',
        time_in_force='gtc',
        side='buy',
        limit_price = 175,
        stop_price = 160
    )


def stop_limit_sell():
    # Submit a market order to buy 1 share of Apple at market price
    api.submit_order(
        symbol='MMM',
        qty=.1,
        type='stop_limit',
        time_in_force='opg',
        side='sell',
        limit_price = 89.60,
        stop_price = 90.04
    )
#sell()
buy()
stop_limit_buy()
#stop_limit_sell()