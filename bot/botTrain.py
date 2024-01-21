#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 17:58:44 2023

@author: lucianoricotta
"""

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
from sklearn.model_selection import train_test_split
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

###############################################################################

def average(lst):
    return sum(lst) / len(lst) 

###############################################################################

def scale(price,total,loss):
    return loss*total/price

###############################################################################

def data_setup(symbol,data_len,seq_len):
    end = datetime.datetime.today().strftime('%Y-%m-%d')
    start = datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.timedelta(days=(data_len))
    orig_dataset = yf.download(symbol,start,end)
    close = orig_dataset['Close'].values
    open_ = orig_dataset['Open'].values
    high = orig_dataset['High'].values
    low = orig_dataset['Low'].values
    dataset,minmax = normalize_data(orig_dataset)
    cols = dataset.columns.tolist()
    
    data_seq = list()
    for i in range(len(cols)):
        if cols[i] < 4:
            data_seq.append(dataset[cols[i]].values)
            data_seq[i] = data_seq[i].reshape((len(data_seq[i]), 1))
    data = hstack(data_seq)
    n_steps = seq_len
    X, y = split_sequences(data, n_steps)
    n_features = X.shape[2]
    n_seq = len(X)
    n_steps = seq_len
    print(X.shape)
    X = X.reshape((n_seq,1, n_steps, n_features))
    true_y = []
    for i in range(len(y)):
        true_y.append([y[i][0],y[i][1]])
    return X,array(true_y),n_features,minmax,n_steps,close,open_,high,low,close[-1]

###############################################################################

def split_sequences(sequences, n_steps):
        X, y = list(), list()
        for i in range(len(sequences)):
            end_ix = i + n_steps
            if end_ix > len(sequences)-1:
                break
            seq_x, seq_y = sequences[i:end_ix, :], sequences[end_ix, :]
            X.append(seq_x)
            y.append(seq_y)
        return array(X), array(y)

###############################################################################

def normalize_data(dataset):
        cols = dataset.columns.tolist()
        col_name = [0]*len(cols)
        for i in range(len(cols)):
            col_name[i] = i
        dataset.columns = col_name
        dtypes = dataset.dtypes.tolist()
#         orig_answers = dataset[attr_row_predict].values
        minmax = list()
        for column in dataset:
            dataset = dataset.astype({column: 'float32'})
        for i in range(len(cols)):
            col_values = dataset[col_name[i]]
            value_min = min(col_values)
            value_max = max(col_values)
            minmax.append([value_min, value_max])
        for column in dataset:
            values = dataset[column].values
            for i in range(len(values)):
                values[i] = (values[i] - minmax[column][0]) / (minmax[column][1] - minmax[column][0])
            dataset[column] = values
        dataset[column] = values
        return dataset,minmax
    
###############################################################################

def enviroment_setup(X,y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
        return X_train, X_test, y_train, y_test

###############################################################################

def initialize_network(n_steps,n_features,optimizer):
    model = Sequential()
    model.add(TimeDistributed(Conv1D(filters=64, kernel_size=1, activation='relu'), input_shape=(None, n_steps, n_features)))
    model.add(TimeDistributed(MaxPooling1D(pool_size=2)))
    model.add(TimeDistributed(Flatten()))
    model.add(LSTM(50, activation='relu'))
    model.add(Dense(2))
    model.compile(optimizer=optimizer, loss='mse')
    return model

###############################################################################

def train_model(X_train,y_train,model,epochs):
    dirx = 'train'
    # Check whether the specified path exists or not
    isExist = os.path.exists(dirx)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(dirx)
    cwd = os.getcwd()
    os.chdir(dirx)
    h5='Stocks'+'_best_model'+'.h5'
    checkpoint = callbacks.ModelCheckpoint(h5, monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=True, mode='auto', period=1)
    earlystop = callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=epochs * 1/4, verbose=0, mode='auto', baseline=None, restore_best_weights=True)
    callback = [earlystop,checkpoint] 
    json = 'Stocks'+'_best_model'+'.json'
    model_json = model.to_json()
    with open(json, "w") as json_file:
        json_file.write(model_json)
    history = model.fit(X_train, y_train, epochs=epochs, batch_size=len(X_train)//4, verbose=0,validation_split = 0.3, callbacks = callback)
    os.chdir(cwd)
    return history

###############################################################################

def load_keras_model(dataset,model,loss,optimizer):
    dirx = 'train'
    # Check whether the specified path exists or not
    isExist = os.path.exists(dirx)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(dirx)
    cwd = os.getcwd()
    os.chdir(dirx)
    json_file = open(dataset+'_best_model'+'.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.compile(optimizer=optimizer, loss=loss, metrics = None)
    model.load_weights(dataset+'_best_model'+'.h5')
    os.chdir(cwd)
    return model

###############################################################################

def evaluation(exe_time,X_test, y_test,X_train, y_train,history,model,optimizer,loss):
    model = load_keras_model('Stocks',model,loss,optimizer)
    test_loss = model.evaluate(X_test, y_test, verbose=0)
    train_loss = model.evaluate(X_train, y_train, verbose=0)
    eval_test_loss = round(100-(test_loss*100),1)
    eval_train_loss = round(100-(train_loss*100),1)
    eval_average_loss = round((eval_test_loss + eval_train_loss)/2,1)
    print("--- Training Report ---")
    #plot_loss(history)
    print('Execution time: ',round(exe_time,2),'s')
    print('Testing Accuracy:',eval_test_loss,'%')
    print('Training Accuracy:',eval_train_loss,'%')
    print('Average Network Accuracy:',eval_average_loss,'%')
    return model,eval_test_loss

###############################################################################

def market_predict(model,minmax,seq_len,n_features,n_steps,data,test_loss):
    pred_data = data[-1].reshape((len(data[-1]),1, n_steps, n_features))
    pred = model.predict(pred_data)[0]
    appro_loss = list()
    for i in range(len(pred)):
        pred[i] = pred[i] * (minmax[i][1] - minmax[i][0]) + minmax[i][0]
        appro_loss.append(((100-test_loss)/100) * (minmax[i][1] - minmax[i][0]))
    return pred,appro_loss


###############################################################################

def create_order(sentiment,pred_price,company,test_loss,appro_loss,time_in_force,price,orders_url,headers,qty,crypto):
    open_price,close_price = pred_price[0],pred_price[1]
    if crypto:
        appro_loss += price*qty*.0025
    print(f"Predicted open price: {open_price}")
    print(f"Predicted close price: {close_price}")
    print("appro loss", appro_loss)
    
    if sentiment < 0:
        side = 'sell'
        side_matrix = [0, 1, 0]
    elif sentiment > 0:
        side = 'buy'
        side_matrix = [1, 0, 0]    
    else:
        print(f'Cannot place stop limit order where open_price {open_price} = close_price {close_price}')
        side_matrix = [0, 0, 1]
        return side_matrix
        
    if side == 'buy':
        print(f"BUY {company} at {price}")
        print('limit_price', close_price + appro_loss[1])
        print('stop_price', close_price - appro_loss[1])
        order = {
            'symbol':company,
            'qty':round(qty*(test_loss/100)),
            'type':'stop_limit',
            'time_in_force': time_in_force,
            'side': side,
            'limit_price': round(close_price + appro_loss[1],2),
            'stop_price': round(close_price - appro_loss[1],2),
            'take_profit': {
              'limit_price': round(close_price + appro_loss[1],2)
            },
            'stop_loss': {
              'stop_price': round(close_price - appro_loss[1],2)
            }
                }
    elif side == 'sell':
        print(f"SELL {company} at {price}")
        print('limit_price', close_price - appro_loss[1])
        print('stop_price', close_price + appro_loss[1])
        order = {
            'symbol':company,
            'qty':round(qty*(test_loss/100)),
            'type':'stop_limit',
            'time_in_force': time_in_force,
            'side': side,
            'limit_price': round(close_price - appro_loss[1],2),
            'stop_price': round(close_price + appro_loss[1],2),
            'take_profit': {
              'limit_price': round(close_price - appro_loss[1],2)
            },
            'stop_loss': {
              'stop_price': round(close_price + appro_loss[1],2)
            }
                }

    print(f"Executing trade...")
    r = requests.post(orders_url, json = order,headers = headers)
    print(r.content)
    
    return side_matrix
    
###############################################################################


