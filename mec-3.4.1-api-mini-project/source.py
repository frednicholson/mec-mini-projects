# program to query data from nasdaq and compute basic statistics
 
from datetime import datetime as dt
import os
import json
from pickle import FALSE
import statistics
import pandas as pd
from tabulate import tabulate

from dotenv import load_dotenv
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from time import strptime

load_dotenv()

#Get the API key which is stored in a file per the instructions

API_KEY = os.getenv('NASDAQ_API_KEY')

Xchange_code = "/XFRA"


# setup query URL via use of variables.  This allows modification of the URL w/o string editing
# 
# #set up variable for ticker specified in the instructions.  However, information for this ticker seems to no longer be free.  Thus, obtained data for a ticker 
# that is included in the current free data set as "ticker2" below
# 
ticker = "/AFX_X"
ticker2 = "/ADS"

outputformat = ".json"

start_date  = "2017-01-01"
end_date    = "2017-12-31"

#Create the URL for querying data based on variables above.
rURL = "http://data.nasdaq.com/api/v3/datasets" + Xchange_code + ticker2 + outputformat + "?" + "&start_date=" + start_date + "&end_date=" + end_date + "&" + "api_key=" + API_KEY

#extract response data
uClient = uReq(rURL)
page_data = uClient.read()
uClient.close()

page_string = str(page_data, 'utf-8')

#convert response to dictionary from json
json_data = json.loads(page_string)

#Extract the time series information from the dictionary derived from the response data
timeseries = json_data["dataset"]["data"]

#setup variables used to track information to be reported.  

highest_open                = 0
first_entry                 = True
daycount                    = 0
biggest_change              = 0
biggest_eod_change          = 0
volume_sum                  = 0
median_list                 = []
prior_date_obj              = dt(2050, 1, 1)
closing_price_list         = []


#Now iterate through each day's stock data, and compute the necessary metrics for each entry.
for entry in timeseries:

    dateobj    = dt.strptime(entry[0], "%Y-%m-%d")
    
    # Set variables based on current entry in timeseries
    open    = float(entry[1])
    high    = float(entry[2])
    low     = float(entry[3])
    close   = float(entry[4])
    volume  = int(entry[5])

    # don't include days with zero closing price
    if close:
        closing_price_list.append((dateobj, close))
   
     
    if open > highest_open: 
        highest_open = open
    if first_entry :
        lowest_open = open
        first_entry = False
    elif open < lowest_open:
        lowest_open = open
    
    #only compute the difference between open and close price if both are non-zero
    if open and close:
        current_change = abs(open - close)
        if current_change > biggest_change :
            biggest_change = current_change
    
  
    #count days and sum the volume for average volume calculation at the end.  Don't include any zero volumes
    if volume:
        daycount += 1
        volume_sum += volume
        #save volume data for median calculation at the end
        median_list.append(volume)


average_volume = volume_sum / daycount

# eod change is based on closing price on two consecutive days.  Assumes entries are in chronological order to avoid storing all closing prices in a list, 
# sorting the list by date, and then computing the bigged_eod_change.
biggest_eod_change = 0

sorted_list = sorted(closing_price_list, key=lambda t: dt.strftime(t[0], '%Y%m%d'), reverse=True)

for tuple in sorted_list:
    current_index = sorted_list.index(tuple)
    # skip the first tuple, and then compare the current tuple to previous tuple, as there is only len-1 comparisons available.
    if current_index:
        eod_change  = abs(tuple[1] - prev_tuple[1])
        if biggest_eod_change < eod_change:
            biggest_eod_change = eod_change
    prev_tuple = tuple
    
    

format_float = "{:.2f}"

stats_dict = {
    'Highest open:' : { 'data' :  format_float.format(highest_open)},
    'Lowest open:'  : { 'data' :  format_float.format(lowest_open)},
    'Largest change between open/close:' : { 'data' : format_float.format(biggest_change) },
    'Largest one day change in closing price:' : { 'data' : format_float.format(biggest_eod_change)},
    'Average volume:' : { 'data' : format_float.format(average_volume)},
    'Median volume:' : { 'data' : statistics.median(median_list) }
}

df = pd.DataFrame(stats_dict)
print(tabulate(df.T))