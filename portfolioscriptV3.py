import bs4 as bs
import json
import pandas as pd
import numpy as np
import requests
import pandas_datareader as web
import datetime as dt
from datetime import date,datetime,timedelta
import pickle
import time
import re

pd.set_option('display.max_columns', 50)

with open('stocks.pickle','rb') as f:
        stocks = pickle.load(f)
with open('reits.pickle','rb') as f:
        reits = pickle.load(f)

stocks_to_add = {}
reits_to_add = {}

if stocks_to_add:
    print("Updating stocks")

    for company in stocks_to_add.keys():
    
        if company[-3:] != ".SI":
            company = company + ".SI"

        company_list = stocks.keys()

        if company in company_list:
            print("Ticker already exist : {} ".format(company))
            continue
        else:
            print("Adding ticker : {} ".format(company))
            company_name = stocks_to_add[company]
            stocks[company] = company_name

    with open('stocks.pickle','wb') as f:
        pickle.dump(stocks,f)

if reits_to_add:
    print("Updating reits")

    for company in reits_to_add.keys():
    
        if company[-3:] != ".SI":
            company = company + ".SI"

        company_list = reits.keys()

        if company in company_list:
            print("Ticker already exist : {} ".format(company))
            continue
        else:
            print("Adding ticker : {} ".format(company))
            company_name = reits_to_add[company]
            reits[company] = company_name

    with open('reits.pickle','wb') as f:
        pickle.dump(reits,f)

def getFinancialData(ticker,ticker_name):
    
    id_ = requests.get("https://ws.investingnote.com/charts/symbols?symbol={}&authenticity_token=C0Wvy6ExIENlWrU6EsuG1Gk3DPWvE1aV%2BmKcY%2BUm5tlaxtEymUtTP6N0O%2FCULjJjkB1Sia9ZlC%2FHZROleaJEyg%3D%3D".format(ticker)).json()['id']
    test = requests.get("https://ws.investingnote.com/charts/history?symbol={}&id={}&resolution=D&from=1519396649&to=1550500710&authenticity_token=C0Wvy6ExIENlWrU6EsuG1Gk3DPWvE1aV%2BmKcY%2BUm5tlaxtEymUtTP6N0O%2FCULjJjkB1Sia9ZlC%2FHZROleaJEyg%3D%3D".format(ticker,id_)).json()

    Open = test['o'][-1]
    High = test['h'][-1]
    Low = test['l'][-1]
    Close = test['c'][-1]
    Vol = test['v'][-1]
    
    lst = [ticker,ticker_name,Close,Open,High,Low,Vol]
    
    return lst

def get_alldata(full_dictionary):

    full_data = []

    for stock in full_dictionary.keys():

        print("Getting data for : {}".format(stock))

        stock_name = full_dictionary[stock]
                
        data = getFinancialData(stock,stock_name)

        full_data.append(data)
        
    return full_data

headers = ["Ticker","Name","Close","Open","High","Low","Volume"]

data = get_alldata({**stocks,**reits})

df = pd.DataFrame.from_records(data,columns=headers)

df.to_csv("data/{}.csv".format(str(date.today())),index=False)