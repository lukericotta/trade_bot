import copy
import datetime
import pandas as pd
import numpy as np
import time
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
nltk.download('vader_lexicon')

def parseTickerNews(tickers, n):
    pd.set_option('display.max_colwidth', 25)
    
    news_tables = {}
    
    for ticker in tickers:
        # Set up scraper
        result = False
        while result is False:
            try:
                url = ("http://finviz.com/quote.ashx?t=" + ticker.lower())
                req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                webpage = urlopen(req).read()
                html = soup(webpage, "html.parser")
                news_table = html.find(id='news-table')
                news_tables[ticker] = news_table
                result = True
            except:
                print(f'Failed to get news data for {ticker}. Trying again...')
                pass
    
    try:
        for ticker in tickers:
            df = news_tables[ticker]
            df_tr = df.findAll('tr')
        
            print ('\n')
            print ('Recent News Headlines for {}: '.format(ticker))
            
            for i, table_row in enumerate(df_tr):
                a_text = table_row.a.text
                td_text = table_row.td.text
                td_text = td_text.strip()
                print(a_text,'(',td_text,')')
                if i == n-1:
                    break
    except KeyError:
        pass
    
    # Iterate through the news
    parsed_news = []
    for file_name, news_table in news_tables.items():
        for x in news_table.findAll('tr'):
            text = x.get_text() 
            date_scrape = x.td.text.split()
    
            if len(date_scrape) == 1:
                time = date_scrape[0]
                
            else:
                date = date_scrape[0]
                time = date_scrape[1]
    
            ticker = file_name.split('_')[0]
            
            parsed_news.append([ticker, date, time, text])
            
    # Sentiment Analysis
    analyzer = SentimentIntensityAnalyzer()
    
    columns = ['Ticker', 'Date', 'Time', 'Headline']
    news = pd.DataFrame(parsed_news, columns=columns)
    scores = news['Headline'].apply(analyzer.polarity_scores).tolist()
    
    df_scores = pd.DataFrame(scores)
    news = news.join(df_scores, rsuffix='_right')
    
    temp = copy.deepcopy(news)
    for i, day in enumerate(temp.Date):
        if day == 'Today':
            news.Date[i] = datetime.date.today()
    
    # View Data 
    news['Date'] = pd.to_datetime(news.Date).dt.date
    
    unique_ticker = news['Ticker'].unique().tolist()
    news_dict = {name: news.loc[news['Ticker'] == name] for name in unique_ticker}
    
    values = []
    for ticker in tickers: 
        dataframe = news_dict[ticker]
        dataframe = dataframe.set_index('Ticker')
        dataframe = dataframe.drop(columns = ['Headline'])
        print ('\n')
        print (dataframe.head())
        
        mean = round(dataframe['compound'].mean(), 2)
        values.append(mean)
        
    df = pd.DataFrame(list(zip(tickers, values)), columns =['Ticker', 'Mean Sentiment']) 
    df = df.set_index('Ticker')
    df = df.sort_values('Mean Sentiment', ascending=False)
    print ('\n')
    print (df)
    return df
    
if __name__ == "__main__":
    parseTickerNews(['BTCUSD', 'ETHUSD'], 5) # pylint: disable=no-value-for-parameter
