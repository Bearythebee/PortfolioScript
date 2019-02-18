import bs4 as bs
import datetime as dt
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
import re

json_key = json.load(open('file.txt')) # json credentials you downloaded earlier

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope) # get email and key from creds

file = gspread.authorize(credentials) # authenticate with Google
sheet = file.open("StockPortfolioTracker") # open sheettest-472@portfolioscript.iam.gserviceaccount.com

Stocks = sheet.worksheet('Stocks')
Reits = sheet.worksheet('REITs')

with open('stocks.pickle','rb') as f:
        stocks = pickle.load(f)
with open('reits.pickle','rb') as f:
        reits = pickle.load(f)


#S$ sign and mm
def str_process(string):
    if string == "-":
        return string
    else:
        return string[3:-3]

def getFinancialData(ticker):
    stock = ticker[:-3]
    options = Options()  
    options.headless = True
    driver = webdriver.Chrome(executable_path='C:\\Users\\Admin\\Desktop\\chromedriver',chrome_options=options)
    
    link = 'https://www2.sgx.com/securities/stock-screener?page=1&code={}&lang=en-us'.format(stock)

    driver.get(link)
    driver.implicitly_wait(60)
    
    
    python_button = driver.find_element_by_xpath("//*[@id='beta-warning-dialog']/div[2]/footer/button")
    python_button.click()
    
    iframe = driver.find_element_by_css_selector("#page-container > template-base > div > div > sgx-widgets-wrapper > widget-stock-screener > iframe")
    driver.switch_to.frame(iframe)
    
    soup = bs.BeautifulSoup(driver.page_source,"html.parser")
    
    driver.close()
    driver.quit()
    
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
    
    
    lst = []
    lst.append(dictionary['5-Year Beta'])
    lst.append((dictionary['Normalized Diluted EPS'])[3:])
    lst.append(dictionary['Adj. 6-month VWAP '][5:10])
    lst.append(dictionary['EV/EBITDA'])
    lst.append(dictionary['Debt/EBITDA'])
    lst.append((dictionary['Shares Outstanding'])[:-3])
    lst.append(str_process(dictionary['Total Market Cap ']))
    lst.append((dictionary['Float'])[:-1])
    lst.append((dictionary['Cap Ex'])[4:-4])
    lst.append(str_process(dictionary['Total Revenue']))
    lst.append(str_process(dictionary['Total Assets']))
    lst.append(str_process(dictionary['Total Debt']))
    lst.append(str_process(dictionary['Net Income']))
    lst.append(str_process(dictionary['Enterprise Value']))
    lst.append(str_process(dictionary['Cash & ST Investments']))
    lst.append(str_process(dictionary['EBITDA']))
    
    return lst

#getFinancialData("ME8U.SI")

def update(sheet,write_counter):
    
    Exempted = ['G3B.SI']
    
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
        
        if stock in Exempted:
            row+=1
            continue
        print("Updating : {} , row {}".format(stock,row))
        
        stock_name = dictionary[stock]
        
        repeat_flag = False
            
        data = getFinancialData(stock)
            
        if ' of\n\n' in data:
            repeat_flag = True
            
        while repeat_flag:
            if ' of\n\n' in data:
                print('##### RETRYING WEBSCRAPE #####')
                data = getFinancialData(stock)
            else:
                repeat_flag = False
            
            
        for col in range(16,32):
                
            sheet.update_cell(row, col, data[col-16])
                
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
update(Reits,0)