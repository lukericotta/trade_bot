#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 12:19:04 2023

@author: lucianoricotta
"""

from apisetup import *
from bot import *
from datetime import datetime
import alpaca_trade_api as tradeapi
import pandas as pd
import requests
import time

AVAILABLE = ['AAVE', 'AVAX', 'BAT', 'BCH', 'BTC', 'CRV', 'DOT', 'ETH', 'GRT', 'LINK', 'LTC', 'MKR', 'SHIB', 'UNI', 'USDC', 'USDT', 'XTZ']
DATA_LEN = 10
EPOCHS = 50
LOSS = 'mse'
OPT='adam'
SEQ_LEN = 2
TO_DROP = ['BRK.B', 'BF.B']
TIME_IN_FORCE = 'gtc'
USD = 10000

def getCrypto():
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
      add = False
      for avail in AVAILABLE:
          if avail in code:
              add = True
      if add:
          coin_list.append(code + '-USD')
      
    df = pd.DataFrame(coin_list, columns=['Symbol'])
    
    return df

def getOrders():
    # Initialize things needed for the while loop
     
    CHUNK_SIZE = 500
    all_orders = []
    start_time = pd.to_datetime('now', utc=True)
    check_for_more_orders = True
     
    while check_for_more_orders:
     # Fetch a 'chunk' of orders and append it to our list
     api_orders = api.list_orders(status='all',
                                        until=start_time.isoformat(),
                                        direction='desc',
                                        limit=CHUNK_SIZE,
                                        nested=False,
                                        )
     all_orders.extend(api_orders)
     
     if len(api_orders) == CHUNK_SIZE:
       # Since length equals the CHUNK_SIZE there may be more orders
       # Set the ending timestamp for the next chunk of orders
       # A hack to work around complex orders having the same submitted_at time
       # and avoid potentially missing one, is to get more than we need
       start_time = all_orders[-3].submitted_at
     
     else:
       # That was the final chunk so exit
       check_for_more_orders = False
     
    # Convert the list into a dataframe and drop any duplicate orders
    orders_df = pd.DataFrame([order._raw for order in all_orders])
    orders_df.drop_duplicates('id', inplace=True)
    
    print("Alpaca orders")
    print(orders_df)
    return orders_df

def train(df, data_len, seq_len):
    X,y,n_features,minmax,n_steps,close,open_,high,low,last_price = data_setup(list(df.Symbol), data_len, seq_len)
    X_train, X_test, y_train, y_test = enviroment_setup(X, y)
    model = initialize_network(n_steps, n_features, OPT)
    start = time.time()
    history = train_model(X_train, y_train, model, EPOCHS)
    exe_time = time.time() - start
    model, test_loss = evaluation(exe_time,X_test, y_test,X_train, y_train,history,model,OPT,LOSS)
    return model, test_loss, minmax, n_features, n_steps

def main():
    crypto = False
    while True:
        if datetime.utcnow().hour > 20:
            break
        
        crypto = not crypto
        
        if crypto:
            df = getCrypto()
        else:
            table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            df = table[0]
            df.to_csv('S&P500-Info.csv')
            df.to_csv("S&P500-Symbols.csv", columns=['Symbol'])
            for drop in TO_DROP:
                df = df.drop(df[df['Symbol'] == drop].index)
            df = df.head(10)
    
        model, test_loss, minmax, n_features, n_steps = train(df, DATA_LEN, SEQ_LEN)    
        my_orders = getOrders()
        for symbol in list(df.Symbol):
            ticker_yahoo = yf.Ticker(symbol)
            data = ticker_yahoo.history()
            last_quote = data['Close'].iloc[-1]
            print(symbol, last_quote)
            X,y,n_features,minmax,n_steps,close,open_,high,low,last_price = data_setup(symbol, DATA_LEN, SEQ_LEN)
            pred,appro_loss = market_predict(model,minmax,SEQ_LEN,n_features,n_steps,X,test_loss)
            create_order(pred,symbol.replace('-',''),test_loss,appro_loss,TIME_IN_FORCE,last_price,USD)
        
            
if __name__ == "__main__":
    main()