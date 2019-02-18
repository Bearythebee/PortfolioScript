import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import requests
import pandas_datareader as web
import bs4 as bs
from datetime import datetime,timedelta
import pickle
import time


def get_distribution(ticker):
	link = "https://sg.finance.yahoo.com/quote/{}/key-statistics?p={}".format(ticker,ticker)
	resp = requests.get(link)

	soup = bs.BeautifulSoup(resp.text,"html.parser")
	price_book = soup.find("td",attrs={"data-reactid": "305"}).text
	#forward_annual_distribution = soup.find("td",class_ = "Fz(s) Fw(500) Ta(end)").text

	return price_book 

print(get_distribution('D05.SI'))