import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import requests
import pandas_datareader as web
import bs4 as bs
from datetime import datetime,timedelta
import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 

json_key = json.load(open('file.txt')) # json credentials you downloaded earlier

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope) # get email and key from creds

file = gspread.authorize(credentials) # authenticate with Google
sheet = file.open("StockPortfolioTracker") # open sheettest-472@portfolioscript.iam.gserviceaccount.com

Stocks = sheet.worksheet('Stocks')
Reits = sheet.worksheet('REITs')

# Updating companies

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

print("####################################")

def getData(ticker,ticker_name):

	Exempted = ["G3B.SI"]

	end = datetime.today()
	start = end - timedelta(days = 365)
	
	df = web.DataReader(ticker,'yahoo',start,end)
	
	lst = [ticker,ticker_name]
	
	lst.append(round(df['Open'][-1],3)) #Open
	lst.append(round(df['High'][-1],3)) #High
	lst.append(round(df['Low'][-1],3)) #Low
	lst.append(round(df['Close'][-1],3)) #Close
	lst.append(round(df['Close'][-2],3)) #Previous Close
	lst.append(round(df['Volume'][-1]/1000,3)) #Volume

	if ticker in Exempted:
		lst.append(round(df['Close'].min(),3)) #52week low
		lst.append(round(df['Close'].max(),3)) #52week High
		lst.append(round(df['Close'].rolling(window = 50,min_periods=0).mean()[-1],3)) #50MA
		lst.append(round(df['Close'].rolling(window = 200,min_periods=0).mean()[-1],3)) #200MA
		lst.append("-")
		lst.append("-")
		lst.append("-")
	
	else:
		link = "https://sg.finance.yahoo.com/quote/{}/key-statistics?p={}".format(ticker,ticker)
		resp = requests.get(link)
		soup = bs.BeautifulSoup(resp.text,"html.parser")

		tables = soup.find_all("table",class_ = "table-qsp-stats Mt(10px)")

		temp_dict = {}

		for table in tables:
			for tr in table:
				for td in tr:
					counter = 0
					heading =""
					for t in td:
						if counter == 0:
							heading = t.text[:-1]
							counter = 1
						else:
							temp_dict[heading] = t.text
							counter = 0

		lst.append(temp_dict["52-week low "]) #52week Low
		lst.append(temp_dict["52-week high "]) #52week High
		lst.append(temp_dict["50-day moving average "]) #50MA
		lst.append(temp_dict["200-day moving average "]) #200MA
		lst.append(temp_dict["Trailing P/E"]) #PE
		lst.append(temp_dict["Price/book (mrq"]) #PB
		lst.append(temp_dict["Trailing annual dividend rate "]) #Div Rate

	return lst

def update(sheet,write_counter):
    
    if sheet == Stocks:
        print("##### Updating stocks #####")
        dictionary = stocks
    if sheet == Reits:
        print("##### Updating reits #####")
        dictionary = reits
    
    row = 3
    
    write_count = write_counter
    
    start_time = time.time()
    
    for stock in dictionary.keys():
        
        print("Updating : {} , row {}".format(stock,row))
        
        stock_name = dictionary[stock]
        
        data = getData(stock,stock_name)
                
        for col in range(1,16):
            
            sheet.update_cell(row, col, data[col-1])
                
            write_count+=1
                
            if write_count == 100:
                time_counter = round(time.time() - start_time)
                sleep_time = 100 - time_counter
                print("Sleeping for {} seconds".format(sleep_time))
                time.sleep(sleep_time)
                write_count = 0
                start_time = time.time()
            
        
        row+=1
        
    return write_count

start = time.time()
write = update(Stocks,0)
#slp = 100-(time.time()-start)
#print("Sleeping for {} seconds".format(slp))
#time.sleep(slp)
update(Reits,write)