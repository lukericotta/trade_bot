#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 12:19:04 2023

@author: lucianoricotta
"""

from apisetup import *
from bot import *
import alpaca_trade_api as tradeapi
import pandas as pd
import requests
import time

CRYPTO = True
available = ['AAVE', 'AVAX', 'BAT', 'BCH', 'BTC', 'CRV', 'DOT', 'ETH', 'GRT', 'LINK', 'LTC', 'MKR', 'SHIB', 'UNI', 'USDC', 'USDT', 'XTZ']

if CRYPTO:
    import requests 
    import json 
    import time 
      
    url = "https://api.livecoinwatch.com/coins/list"
      
    payload = json.dumps({ 
      "currency": "USD", 
      "sort": "rank", 
      "order": "ascending", 
      "offset": 0, 
      "limit": 100, 
      "meta": True
    }) 
    headers = { 
      'content-type': 'application/json', 
      'x-api-key': 'c421fb1a-ce3b-4e9c-ad99-dd99981e9526'
    } 
      
    response = requests.request("POST", url,  
                                headers=headers,  
                                data=payload) 
    response_json = response.json() 
      
    i = 0
    print("Top 100 Coins:\n")
    coin_list = []
    while i <100 : 
      this = response_json[i] 
      rank = this['rank'] 
      name = this['name'] 
      code = this['code'] 
      volume = this['volume'] 
      rate = this['rate'] 
      link = "https://livecoinwatch.com/price/" + name.replace(" ", "") + "-" + code 
      ts = time.gmtime() 
      print(str(rank) + '. ' + name + " ${:,.2f}".format(rate) + " Volume: ${:,.2f}".format(volume) + " " + time.asctime(ts) + "\n" + link + "\n") 
      i += 1
      coin_list.append(code + '-USD')
      
    df = pd.DataFrame(coin_list, columns=['Symbol'])
      
else:
    table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = table[0]
    df.to_csv('S&P500-Info.csv')
    df.to_csv("S&P500-Symbols.csv", columns=['Symbol'])
    to_drop = ['BRK.B', 'BF.B']
    for drop in to_drop:
        df = df.drop(df[df['Symbol'] == drop].index)

# Define the stock symbol and time frame
timeframe = '1D'
data_len = 1000
seq_len = 10
epochs = 100
optimizer='adam'
loss = 'mse'
time_in_force = 'gtc'
usd = 100

while True:
    for symbol in list(df.Symbol):
        skip = True
        for avail in available:
            if avail in symbol:
                skip = False
        if skip:
            continue
        X,y,n_features,minmax,n_steps,close,open_,high,low,last_price = data_setup(symbol, data_len, seq_len)
        X_train, X_test, y_train, y_test = enviroment_setup(X, y)
        model = initialize_network(n_steps, n_features, optimizer)
        start = time.time()
        history = train_model(X_train, y_train, model, epochs)
        exe_time = time.time() - start
        model, test_loss = evaluation(exe_time,X_test, y_test,X_train, y_train,history,model,optimizer,loss)
        ticker_yahoo = yf.Ticker(symbol)
        data = ticker_yahoo.history()
        last_quote = data['Close'].iloc[-1]
        print(symbol, last_quote)

        pred,appro_loss = market_predict(model,minmax,seq_len,n_features,n_steps,X,test_loss)
        create_order(pred,symbol.replace('-',''),test_loss,appro_loss,time_in_force,last_price,usd)
        
        
        