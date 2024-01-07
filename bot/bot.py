"""
BoptimalTrader
"""

from alpaca.trading.client import TradingClient
from .botFunctions import *
from .botTrain import *
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras import callbacks
from keras.layers import Flatten
from keras.layers import TimeDistributed
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.models import model_from_json
from keras.models import load_model
from IPython.display import clear_output
from matplotlib import pyplot as plt
from numpy import array
from numpy import hstack
from operator import add
from sklearn.model_selection import train_test_split
import alpaca_trade_api as tradeapi
import datetime
import json
import os
import pandas as pd
import random
import requests
import statistics
import time
import yaml
import yfinance as yf


class BoptimalTrader():
    """
    BoptimalTrader
    
    Args:
      string: API yaml configuration file
      string: training yaml configuration file
      bool: crypto
    """
    def __init__(self, api_config, training_config, crypto):
      self.api_config = self.loadYaml(api_config)
      self.training_config = self.loadYaml(training_config)
      self.crypto = crypto      
      
    def loadYaml(self, path):
        with open(path, "r") as yamlfile:
            data = yaml.load(yamlfile, Loader=yaml.FullLoader)
        return data
    
    def setup(self):
        self.API_KEY = self.api_config['Key']
        self.API_SECRET = self.api_config['SecretKey']
        self.BASE_URL = self.api_config['BaseURL']
        self.ORDERS_URL = '{}/v2/orders'.format(self.BASE_URL)
        self.HEADERS = {'APCA-API-KEY-ID':self.API_KEY,'APCA-API-SECRET-KEY':self.API_SECRET}
        self.api = tradeapi.REST(self.API_KEY, self.API_SECRET, base_url=self.BASE_URL, api_version='v2')
        self.trading_client = TradingClient(self.API_KEY, self.API_SECRET)
        self.AVAILABLE = self.training_config['Available']
        self.LOSS = self.training_config['Loss']
        self.OPT = self.training_config['Optimizer']
        self.SEQ_LEN = self.training_config['SeqLen']
        self.TIME_IN_FORCE = self.training_config['TimeInForce']
        self.TO_DROP = self.training_config['ToDrop']
        self.DATA_LEN = self.training_config['DataLen']
        self.EPOCHS = self.training_config['Epochs']
        self.QTY = self.training_config['Quantity']

    def train(self, sym, data_len, seq_len):
        X,y,n_features,minmax,n_steps,close,open_,high,low,last_price = data_setup(sym, data_len, seq_len)
        X_train, X_test, y_train, y_test = enviroment_setup(X, y)
        model = initialize_network(n_steps, n_features, self.OPT)
        start = time.time()
        history = train_model(X_train, y_train, model, self.EPOCHS)
        exe_time = time.time() - start
        model, test_loss = evaluation(exe_time,X_test, y_test,X_train, y_train,history,model,self.OPT,self.LOSS)
        return model, test_loss, minmax, n_features, n_steps

    def start(self):
        side_count= [0, 0, 0]

        # First wait until not after hours
        while afterHours() and not self.crypto:
            continue

        self.api.cancel_all_orders()
        while not afterHours() or self.crypto:
            try:
                my_orders = getOrders(self.api)
                
                if self.crypto:
                    df = getCrypto(self.AVAILABLE)
                else:
                    table=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
                    df = table[0]
                    df.to_csv('S&P500-Info.csv')
                    df.to_csv("S&P500-Symbols.csv", columns=['Symbol'])
                    for drop in self.TO_DROP:
                        df = df.drop(df[df['Symbol'] == drop].index)
                    
                symbols_to_trade = [pos.symbol for pos in self.trading_client.get_all_positions()] + list(df.Symbol)
                random.shuffle(symbols_to_trade)
                for symbol in symbols_to_trade:
                    try:
                        ticker_yahoo = yf.Ticker(symbol)
                        data = ticker_yahoo.history()
                        last_quote = data['Close'].iloc[-1]
                        print(symbol, last_quote)
                        account = self.api.get_account()
                        if float(account.portfolio_value) < float(last_quote):
                            continue
                        elif float(account.buying_power) < float(last_quote):
                            self.api.cancel_all_orders()
                            account = self.api.get_account()
                            if not self.crypto and float(account.buying_power) < float(last_quote):
                                self.api.close_all_positions()
                        model, test_loss, minmax, n_features, n_steps = self.train(symbol, self.DATA_LEN, self.SEQ_LEN)
                        X,y,n_features,minmax,n_steps,close,open_,high,low,last_price = data_setup(symbol, self.DATA_LEN, self.SEQ_LEN)
                        pred,appro_loss = market_predict(model,minmax, self.SEQ_LEN,n_features,n_steps,X,test_loss)
                        open_orders = [o for o in self.api.list_orders(status='open') if o.symbol == symbol]
                        for order in open_orders:
                            self.api.cancel_order(order.id)
                        side = create_order(pred,symbol.replace('-',''),test_loss,appro_loss,self.TIME_IN_FORCE,last_price,self.ORDERS_URL,self.HEADERS,self.QTY,self.crypto)
                        side_count = list( map(add, side_count, side) )
                    except KeyboardInterrupt:
                        print("Trading stopped.")
                        break
                    except Exception as e:
                        print(f"Execution of trade with {symbol} failed for unknown reason")
                        print(e)
                    finally:
                        if beforeHours(self.crypto, self.api):
                            break
                else:
                    continue
                break
            except Exception as e:
                print(f"Exception occurred: ")
                print(e)
        self.api.cancel_all_orders()
        if not self.crypto:
            self.api.close_all_positions()

        print("Counts for buy, sell, hold: ", side_count)    

