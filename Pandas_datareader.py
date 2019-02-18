import pandas as pd
import numpy as np
import requests
import pandas_datareader as web
import datetime as dt
from datetime import date, datetime,timedelta
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

	end = datetime.today()
	start = end - timedelta(days = 200)

	df = web.DataReader(ticker,'yahoo',start,end)


	Open = round(df['Open'][-1],3) #Open
	High = round(df['High'][-1],3) #High
	Low = round(df['Low'][-1],3) #Low
	Close = round(df['Close'][-1],3) #Close
	Vol = round(df['Volume'][-1]/1000,3)

	lst = [ticker,ticker_name,Close,Open,High,Low,Vol]

	print(lst)

	return lst

#getFinancialData("5WE.SI","MOYA ASIA")

print(str(date.today()))