#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 20:15:18 2023

@author: lucianoricotta
"""

from apisetup import *
import pandas as pd

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

orders_df.query("symbol == 'AAPL' and filled_at != 10")