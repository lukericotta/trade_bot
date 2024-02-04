#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 21 11:16:16 2024

@author: lucianoricotta
"""

from alpaca.trading.requests import GetPortfolioHistoryRequest
from alpaca.trading.client import TradingClient
from alpaca.common.enums import BaseURL
from typing import Optional, List, Union
from alpaca.trading.models import PortfolioHistory
from alpaca.common import RawData

import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime as dt

import pandas as pd
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta

import holidays, pytz

class TradingClientPortfolioAble(TradingClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        paper: bool = True,
       
    ) -> None:

        super().__init__(
            api_key=api_key,
            secret_key=secret_key,
            paper=paper
        )
    
    def get_portfolio_history(
        self, filter: Optional[GetPortfolioHistoryRequest] = None
    ) -> Union[PortfolioHistory, RawData]:
        """
        Gets the portfolio history statistics.

        Args:
            filter (Optional[GetPortfolioHistoryRequest]): The parameters to filter the history with.

        Returns:
            PortfolioHistory: The portfolio history statistics for the account.
        """
        # checking to see if we specified at least one param
        params = filter.to_request_fields() if filter else {}

        response = self.get("/account/portfolio/history", params)

        if self._use_raw_data:
            return response

        return PortfolioHistory(**response)

def isHoliday(now):
    # If a holiday
    us_holidays = holidays.US()
    if now.strftime('%Y-%m-%d') in us_holidays:
        return True

def plotAlpaca(start_date, key, secret):
    n = dt.date.today() - start_date
    n = n.days
    start = dt.datetime.now() - relativedelta(years=1)
    end = dt.date.today()
    SP500 = web.DataReader(['sp500'], 'fred', start, end)
    
    SP500['daily_return'] = (SP500['sp500']/ SP500['sp500'].shift(1)) -1

    #Drop all Not a number values using drop method.
    SP500 = SP500.tail(n).drop(columns=['daily_return'])

    SP500.dropna(inplace = True)
        
    period = len(SP500['sp500'])
    
    SP500['sp500'].plot(title='S&P 500 Yearly Return')
        
    spList = []
    spDates = []
    indexList = []
    for index, row in SP500.iterrows():
        indexList.append(index)
        d = start_date
        start_datetime = dt.datetime(d.year, d.month, d.day)
        if isHoliday(index.to_pydatetime()):
            spList.append(spList[-1])
        elif index.to_pydatetime() >= start_datetime:
            spList.append(row['sp500'])
            spDates.append(index)
    
    spFirst = spList[0]
    spList = [price*1000000/spFirst for price in spList]
    
    plt.plot(spList, 'b-')
    
    trading_client = TradingClientPortfolioAble(key, secret, paper=True)
    portFilter = GetPortfolioHistoryRequest(extended_hours=True, period=f'{n}D', timeframe='1D')
    portHistory=trading_client.get_portfolio_history(filter=portFilter)
    print(portHistory)
    
    plt.plot(portHistory.equity, "r-", alpha=0.5, label="Trade Bot")
    plt.plot(spList, "b-", alpha=0.5, label="S&P 500")
    plt.show()
        
    dates=[dt.datetime.fromtimestamp(ts) for ts in portHistory.timestamp]
    datenums=md.date2num(dates)
    ax=plt.gca()
    xfmt = md.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(datenums,portHistory.equity, "r-", alpha=0.5, label="Trade Bot")
    plt.plot(datenums,spList, "b-", alpha=0.5, label="S&P 500")
    plt.show()
    
    plt.xlabel('Time')
    plt.ylabel('Equity')
    plt.title(f'Portfolio Value on {dt.date.today().strftime("%b-%d-%Y")}')
    plt.grid(True)
    ax=plt.gca()
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(datenums,portHistory.equity, "r-", alpha=0.5, label="Trade Bot")
    plt.plot(datenums,spList, "b-", alpha=0.5, label="S&P 500")
    plt.legend(loc="upper left")
        
    return plt

if __name__ == "__main__":
    plt = plotAlpaca(dt.date(2024,1,29), 'PKMKQR4K6AHO51JD6X3S', 'TvtrNsGCRnmi1KH9zt3feQMhuitbcbU19ddndnIa') # pylint: disable=no-value-for-parameter
    plt.show()