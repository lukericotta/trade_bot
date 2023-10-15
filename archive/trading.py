from alpaca_trade_api.rest import REST, TimeFrame
from datetime import datetime, timedelta
import datetime
import math
import time
import pandas as pd
import alpaca_trade_api as tradeapi

# Set your Alpaca API key and secret
API_KEY = 'PKVPQAE15P6TVYEP3A0F'
API_SECRET = 'QH4P6UP0J5S2NMw0qJhYD5OvYVrnaGtecl3c76T3'
BASE_URL = 'https://paper-api.alpaca.markets'  # For paper trading
api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

SYMBOL = 'AAPL'
SMA_FAST = 12
SMA_SLOW = 24
QTY_PER_TRADE = 1

# Description is given in the article
def get_pause():
    now = datetime.now()
    next_min = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    pause = math.ceil((next_min - now).seconds)
    print(f"Sleep for {pause}")
    return pause

# Same as the function in the random version
def get_position(symbol):
    positions = api.list_positions()
    for p in positions:
        if p.symbol == symbol:
            return float(p.qty)
    return 0

# Returns a series with the moving average
def get_sma(series, periods):
    return series.rolling(periods).mean()

# Checks whether we should buy (fast ma > slow ma)
def get_signal(fast, slow):
    print(f"Fast {fast[-1]}  /  Slow: {slow[-1]}")
    return fast[-1] > slow[-1]

# Get up-to-date 1 minute data from Alpaca and add the moving averages
def get_bars(symbol):
    bars = api.get_bars(symbol, TimeFrame.Minute).df
    bars = bars[bars.exchange == 'CBSE']
    bars[f'sma_fast'] = get_sma(bars.close, SMA_FAST)
    bars[f'sma_slow'] = get_sma(bars.close, SMA_SLOW)
    return bars

while True:
    # GET DATA
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    bars = api.get_bars(SYMBOL, TimeFrame.Minute)
    #bars = api.get_bars(SYMBOL, '1Min', start=start_date, end=end_date)
    #bars = get_bars(symbol=SYMBOL)
    # CHECK POSITIONS
    position = get_position(symbol=SYMBOL)
    should_buy = get_signal(bars.sma_fast,bars.sma_slow)
    print(f"Position: {position} / Should Buy: {should_buy}")
    if position == 0 and should_buy == True:
        # WE BUY ONE BITCOIN
        api.submit_order(SYMBOL, qty=QTY_PER_TRADE, side='buy')
        print(f'Symbol: {SYMBOL} / Side: BUY / Quantity: {QTY_PER_TRADE}')
    elif position > 0 and should_buy == False:
        # WE SELL ONE BITCOIN
        api.submit_order(SYMBOL, qty=QTY_PER_TRADE, side='sell')
        print(f'Symbol: {SYMBOL} / Side: SELL / Quantity: {QTY_PER_TRADE}')

    time.sleep(get_pause())
    print("*"*20)