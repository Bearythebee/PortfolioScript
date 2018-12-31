# Portfolio_Script
Script written to update data on google sheets

Wrote a script to update stock market prices on my own google sheet

Daily data taken from pandas yahoo datareader(pandas) and scraped from yahoo finance website(Beautiful Soup)

Company's financial data  taken from SGX website. (Selenium and BeautifulSoup)

Problems encountered:
 - Unable to update stock price in realtime (Still working on it)
 - Unable to scrape data from some websites with just BeautifulSoup
    - some data are updated regularly with javascript / hidden in an iframe 
    - managed to solve it utilising Selenium and chromedriver
 - Updating limit for google sheets - 100 writes per 100 seconds
    - Allowed code to sleep for a certain amount of time in between updates to bypass this limit.
 
 Still trying to improve on data collection
     - Exploring other financial websites (MorningStar,FinancialTimes etc.)
