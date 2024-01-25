#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 11:26:58 2024

@author: lucianoricotta
"""

import pandas as pd
#if you get an error after executing the code, try adding below. pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import datetime
from dateutil.relativedelta import relativedelta

def plotSP500():
    start = datetime.datetime.now() - relativedelta(years=1)
    end = datetime.date.today()
    SP500 = web.DataReader(['sp500'], 'fred', start, end)
    
    SP500['daily_return'] = (SP500['sp500']/ SP500['sp500'].shift(1)) -1
    
    #Drop all Not a number values using drop method.
    SP500.dropna(inplace = True)
    
    SP500['sp500'].plot(title='S&P 500 Yearly Return')
    
    return SP500

if __name__ == "__main__":
    plotSP500() # pylint: disable=no-value-for-parameter