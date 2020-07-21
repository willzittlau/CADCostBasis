# Import Libraries
import pandas as pd
import requests
import datetime
import json

# Intro
print ('This program will take a user portfolio in mixed-currency equities and change it to CAD based with additional info')
input ('Press \'Enter\' to Continue')
print ("Working ...")

# Take CSV and turn into pandas dataframe
data = pd.read_csv('quotes.csv')

# Make new DF of select columns (pf=portfolio)
pf = pd.DataFrame(data, columns= ['Symbol','Current Price', 'Purchase Price', 'Trade Date', 'Quantity'])
# Update 'Trade Date' to date time type
pf['Trade Date'] = pd.to_datetime(pf['Trade Date'], format='%Y%m%d')

# Seperate Cdn and US equities by defining str
cdn1 = '.TO'
cdn2 = '.V'

# Cost Basis calculation
for i in range(0,len(pf['Purchase Price'])):
    # I assume here if purchase price exists then a symbol does as well
    # if .TO is not in symbol OR .V is not in symbol, then
    if not cdn1 in pf.at[i,'Symbol'] or cdn2 in pf.at[i,'Symbol']:
        # Update price based on exchange rate
        rh = requests.get('https://api.exchangeratesapi.io/%s?base=USD&symbols=CAD' 
                          % pf.at[i,'Trade Date'].date())
        jh = rh.json()
        xh = float(jh['rates']['CAD'])
        pf.at[i,'Purchase Price'] = xh * (pf.at[i,'Purchase Price'])

# Define live currency exchange
r = requests.get('https://api.exchangeratesapi.io/latest?base=USD&symbols=CAD')
j = r.json()
x = float(j['rates']['CAD'])

# US/CAD Current Price calculation
for i in range(0,len(pf['Current Price'])):
    # I assume here if current price exists then a symbol does as well
    # if .TO is not in symbol OR .V is not in symbol, then
    if not cdn1 in pf.at[i,'Symbol'] or cdn2 in pf.at[i,'Symbol']:
        # update price based on exchange rate
        pf.at[i,'Current Price'] = x * pf.at[i,'Current Price']

# Calculate total value, gain, and percent of portfolio, append to DF
# Total Value calculation
totval = pf['Current Price'] * pf['Quantity']
pf['Total Value'] = totval

# Weight of Portfolio calculation
pft= pf['Total Value'].sum()
wt = pf['Total Value'] / pft * 100
pf ['Weight %'] = wt

# Gain formula
glp = pf['Current Price'] / pf['Purchase Price'] * 100
pf ['Gain/Loss %'] = glp
# Changes % to negative if loss, and 0 as base instead of 100 if no change / gain
for i in range(0,len(pf['Gain/Loss %'])):
    if pf.at[i,'Gain/Loss %'] >= 100.0:
        pf.at[i,'Gain/Loss %'] = pf.at[i,'Gain/Loss %'] - 100
    else:
        pf.at[i,'Gain/Loss %'] = - (100 - pf.at[i,'Gain/Loss %'])

# Clean up table
del pf['Trade Date']
pf['Current Price'] = pf['Current Price'].round(decimals=2)
pf['Purchase Price'] = pf['Purchase Price'].round(decimals=2)
pf['Total Value'] = pf['Total Value'].round(decimals=2)
pf['Weight %'] = pf['Weight %'].round(decimals=2)
pf['Gain/Loss %'] = pf['Gain/Loss %'].round(decimals=2)

# Output
print (pf)
print ("Total Portfolio Value: $" + '%.2f' %pft +' CAD')