import bs4 as bs
import datetime as dt
import json
import pandas as pd
import numpy as np
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import requests
import pandas_datareader as web
import bs4 as bs
import datetime as dt
from datetime import datetime,timedelta
import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

pd.set_option('display.max_columns', 50)

#json_key = json.load(open('file.txt')) # json credentials you downloaded earlier

#scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope) # get email and key from creds

#file = gspread.authorize(credentials) # authenticate with Google
#sheet = file.open("StockPortfolioTracker") # open sheettest-472@portfolioscript.iam.gserviceaccount.com

#Stocks = sheet.worksheet('Stocks')
#Reits = sheet.worksheet('REITs')

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

def parse(x):
        return x.split("-")

def getFinancialData(ticker,ticker_name):
    
    #Options for chromedriver
    options = Options()  
    options.headless = True

    #Initiating chromedriver
    driver = webdriver.Chrome(executable_path='C:\\Users\\Admin\\Desktop\\chromedriver',chrome_options=options)
    
    #For link
    stock = ticker[:-3]
    
    link = 'https://www2.sgx.com/securities/stock-screener?page=1&code={}&lang=en-us'.format(stock)

    driver.get(link)
    driver.implicitly_wait(60)
    
    #Clearing Pop-up
    python_button = driver.find_element_by_xpath("//*[@id='beta-warning-dialog']/div[2]/div/div/div/div[3]/button")
    python_button.click()
    
    #Finding table
    iframe = driver.find_element_by_css_selector("#page-container > template-base > div > div > sgx-widgets-wrapper > widget-stock-screener > iframe")
    driver.switch_to.frame(iframe)
    
    soup = bs.BeautifulSoup(driver.page_source,"html.parser")
    
    driver.close()
    driver.quit()
    
    flag=False

    curr_price = soup.find('span',class_="price")

    if curr_price == None:
        flag=True
    
    
    while flag:
        print('##### Re-scraping data for {} #####'.format(ticker))
        options = Options()  
        options.headless = True

        #Initiating chromedriver
        driver = webdriver.Chrome(executable_path='C:\\Users\\Admin\\Desktop\\chromedriver',chrome_options=options)

        #For link
        stock = ticker[:-3]

        link = 'https://www2.sgx.com/securities/stock-screener?page=1&code={}&lang=en-us'.format(stock)

        driver.get(link)
        driver.implicitly_wait(60)

        #Clearing Pop-up
        python_button = driver.find_element_by_xpath("//*[@id='beta-warning-dialog']/div[2]/div/div/div/div[3]/button")
        python_button.click()

        #Finding table
        iframe = driver.find_element_by_css_selector("#page-container > template-base > div > div > sgx-widgets-wrapper > widget-stock-screener > iframe")
        driver.switch_to.frame(iframe)
        
        soup = bs.BeautifulSoup(driver.page_source,"html.parser")

        driver.close()
        driver.quit()

        curr_price = soup.find('span',class_="price")

        if curr_price==None:
            flag=True
        else:
            flag=False


    main = soup.find('div',class_='tab-content')
    tabs = main.findAll('div')
    
    dictionary = {}
    
    for tab in range(0,3):
    	table = tabs[tab].find('tbody').findAll('td')
    	count = 1
    	name = ""
    	flag = False
    	for td in table:
    		if count == 1:
    			if flag == True:
    				flag=False
    				continue
    			if td.text == 'Unadj. 6-month VWAP ' or td.text == 'Adj. 6-month VWAP ':
    				flag = True
    			name = td.text
    			count+=1
    		else:
    			dictionary[name] = td.text
    			count=1
    			name=""

    
    lst = [ticker,ticker_name,curr_price.text]

    #Open
    lst.append(dictionary['Previous Open Price'][3:])

    #Day high and Low
    dayhighlow = parse(dictionary['Previous Day High/Low'])
    lst.append(dayhighlow[0][3:])
    lst.append(dayhighlow[1][3:])

    #Close
    lst.append(dictionary['Previous Close'][3:])

    #Volume
    lst.append(dictionary['Previous Day Volume'])

    #52Week High Low
    yearhighlow = parse(dictionary['52 Week High/Low'])
    lst.append(yearhighlow[1][3:])
    lst.append(yearhighlow[0][3:])

    #PE Ratio
    lst.append(dictionary['P/E Ratio'])

    #PB Ratio
    lst.append(dictionary['Price/Book Value'])

    #Dividend Yield
    Yield = dictionary['Dividend Yield ']
    if Yield == "-":
        lst.append(Yield)
    else:
        lst.append(str(float(Yield[:-1])/100))
    
    print(lst)
    
    return lst

def get_alldata(full_dictionary):
    
    Exempted = ['G3B.SI']

    full_data = []

    for stock in full_dictionary.keys():

        print("Getting data for : {}".format(stock))

        stock_name = full_dictionary[stock]
        
        if stock in Exempted:
            
            end = datetime.today()
            start = end - timedelta(days = 200)
        
            df = web.DataReader(stock,'yahoo',start,end)

            data = [stock,stock_name]
            data.append(round(df['Close'][-1],3)) #Close
            data.append(round(df['Open'][-1],3)) #Open
            data.append(round(df['Low'][-1],3)) #Low
            data.append(round(df['High'][-1],3)) #High
            data.append(round(df['Close'][-2],3)) #PrevClose
            data.append(round(df['Volume'][-1]/1000,3)) #Volume
            data.append(round(df['Close'].min(),3)) #52week low
            data.append(round(df['Close'].max(),3)) #52week High
            data.append("-")
            data.append("-")
            data.append("-")

            full_data.append(data)

        else:
            
            repeat_flag = False
                
            data = getFinancialData(stock,stock_name)

            test_data = set(data[2:])

            if test_data == set(["-",""]):
                repeat_flag = True
                
            while repeat_flag:
                if test_data == set(["-",""]):
                    print('##### Re-scraping data for {} #####'.format(stock))
                    data = getFinancialData(stock,stock_name)
                    test_data = set(data[2:])
                else:
                    repeat_flag = False

            full_data.append(data)
        
    return full_data

headers = ["Ticker","Name","Close","Prev_Open","Prev_Low","Prev_High","Prev_Close","Prev_Volume","52week Low","52week High","PE Ratio","PB Ratio","Dividend Yield"]

data = get_alldata({**stocks,**reits})

df = pd.DataFrame.from_records(data,columns=headers)

df.to_csv("data/data.csv",index=False)