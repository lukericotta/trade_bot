#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 13:39:19 2023

@author: lucianoricotta
"""

import alpaca_trade_api as tradeapi
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import datetime
import numpy as np

# Set your Alpaca API key and secret
API_KEY = 'PKVPQAE15P6TVYEP3A0F'
API_SECRET = 'QH4P6UP0J5S2NMw0qJhYD5OvYVrnaGtecl3c76T3'
BASE_URL = 'https://paper-api.alpaca.markets'  # For paper trading
api = tradeapi.REST(API_KEY, API_SECRET, base_url=BASE_URL, api_version='v2')

# Define the stock symbol and time frame
symbol = 'AAPL'
timeframe = '1D'

# Fetch historical data
start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
all_data = api.get_bars(symbol, timeframe, start=start_date, end=end_date)
stock_data = all_data.df[symbol]

# Feature engineering
stock_data['SMA_50'] = stock_data['close'].rolling(window=50).mean()
stock_data['SMA_200'] = stock_data['close'].rolling(window=200).mean()
stock_data.dropna(inplace=True)

# Create features and labels
X = stock_data[['SMA_50', 'SMA_200']].values
y = np.where(stock_data['close'].shift(-1) > stock_data['close'], 1, 0)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train a machine learning model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions on the test set
predictions = model.predict(X_test)

# Evaluate the accuracy of the model
accuracy = accuracy_score(y_test, predictions)
print(f'Model Accuracy: {accuracy}')

# Make a prediction for the current data point
current_data = np.array([[stock_data['SMA_50'].iloc[-1], stock_data['SMA_200'].iloc[-1]]])
current_data = scaler.transform(current_data)
prediction = model.predict(current_data)

# Implement a basic trading strategy based on the prediction
if prediction == 1:
    # Buy signal
    api.submit_order(
        symbol=symbol,
        qty=1,
        side='buy',
        type='market',
        time_in_force='gtc',
    )
else:
    # Sell signal
    api.submit_order(
        symbol=symbol,
        qty=1,
        side='sell',
        type='market',
        time_in_force='gtc',
    )