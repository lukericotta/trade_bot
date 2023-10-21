#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 14 16:25:21 2023

@author: lucianoricotta
"""

import datetime, pytz, holidays
import json
import pandas as pd
import requests
import time

def afterHours():
    tz = pytz.timezone('US/Eastern')
    us_holidays = holidays.US()
    openTime = datetime.time(hour = 9, minute = 30, second = 0)
    closeTime = datetime.time(hour = 16, minute = 0, second = 0)
    now = datetime.datetime.now(tz)
    # If a holiday
    if now.strftime('%Y-%m-%d') in us_holidays:
        return True
    # If before 0930 or after 1600
    if (now.time() < openTime) or (now.time() > closeTime):
        return True
    # If it's a weekend
    if now.date().weekday() > 4:
        return True
    
    return False    

def beforeHours():
    tz = pytz.timezone('US/Eastern')
    us_holidays = holidays.US()
    openTime = datetime.time(hour = 9, minute = 30, second = 0)
    preOpenTime = datetime.time(hour = 9, minute = 25, second = 0)
    now = datetime.datetime.now(tz)
    # If a holiday
    if now.strftime('%Y-%m-%d') in us_holidays:
        return False
    # If it's a weekend
    if now.date().weekday() > 4:
        return False
    # If before 0930 and after 925
    if (now.time() < openTime) and (now.time() > preOpenTime):
        return True
    
    return False  

def close_all_positions_end_of_day():
    #  First, check if the market is currently open. No point in checking if closed.
    if api.get_clock().is_open:
        #  Get the current time (New York time)
        time_now = dt.datetime.now(pytz.timezone('US/Eastern'))

        #  Calculate the timestamp for 5 mins before close (15:55) today.
        five_mins_before_end_of_day = pd.Timestamp(year=time_now.year, month=time_now.month, day=time_now.day, hour=15,
                                                   minute=55, second=00, tz='US/Eastern')

        #  If the current time is the same as (or after) 15:55, close all positions.
        if time_now.isoformat() >= five_mins_before_end_of_day.isoformat():
            print('Closing all positions...')
            api.close_all_positions()
            return True
        else:
            print('Not yet 3:55pm!')
    else:
        print('Market currently closed!')
        
    return False
        
def getCrypto(available):
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
      for avail in available:
          if avail in code:
              add = True
      if add:
          coin_list.append(code + '-USD')
      
    df = pd.DataFrame(coin_list, columns=['Symbol'])
    
    return df

def getOrders(api):
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
