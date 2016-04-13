#############################################
# Market simulation as detailed within
#
# http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_7
#
# python 3_marketsim.py 100000 orders.csv values.csv
#
#############################################

import sys
import csv
import math
import pandas as pd
import numpy as np
import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu

if __name__ == '__main__':
    
    cash = int(sys.argv[1])
    orders_file = sys.argv[2]
    values_file = sys.argv[3]
    
    print 'Using Cash Budget:', cash
    print 'Using Orders file:', orders_file
    print 'Using Values file:', values_file

    # 1 - Read CSV into "trades" array
    #     - Build list of symbols
    #     - Build date boundaries

    with open(orders_file, 'r') as f:
        reader = csv.reader(f)
        trades = list(reader)

    # Create an array of symbols
    symbols = []
    traded_dates = []

    for i in range(0, np.shape(trades)[0]):

        # Add the symbol if it hasn't been added already
        symbol = trades[i][3].strip()
        
        if symbol not in symbols:
            symbols.append(symbol)
            
        # Create an entry in the traded_dates
        i_year = int(trades[i][0].strip())
        i_month = int(trades[i][1].strip())
        i_day = int(trades[i][2].strip())
        dt_trade_date = dt.datetime(i_year, i_month, i_day)
        
        i_amount = int(trades[i][5].strip())
        
        # positive values are buys, negative are sells
        buy_or_sell = trades[i][4].strip()
        if buy_or_sell.upper() == "SELL":
            i_amount = -i_amount
        
        if 'period_start' in locals():
            if period_start > dt_trade_date:
                period_start = dt_trade_date
        else:
            period_start = dt_trade_date

        if 'period_end' in locals():
            if period_end < dt_trade_date:
                period_end = dt_trade_date
        else:
            period_end = dt_trade_date
            
        # Stored items as symbol index, date and amount
        traded_dates.append([dt_trade_date, symbols.index(symbol), i_amount])
        
    # Sort the traded dates by date order
    traded_dates.sort(key=lambda trade: trade[0])
    traded_dates = np.array(traded_dates)

    # Add a day to the datetime
    period_start = period_start + dt.timedelta(hours=16)
	
    period_end = period_end + dt.timedelta(days=1)
    period_end = period_end + dt.timedelta(hours=16)
    
    # print traded_dates
    print "Trading symbols:" + str(symbols)
    print "From:" + str(period_start)
    print "To:" + str(period_end)
    
    # 3 - Read in data
    #     - Read in adjusted close

    ldt_timestamps = du.getNYSEdays(period_start, period_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    # Read in adjusted closing prices for the equities.
    adjusted_close_price = d_data['close'].values
    
    timestamps = np.array(ldt_timestamps)
    timestamps = timestamps.reshape((timestamps.size, 1))
    adjusted_close_price = np.concatenate((adjusted_close_price, timestamps), axis = 1)

    # 4 - Scan trades to update cash
    #     - BUY is a cash reduction
    #     - SELL is a cash increase based on date
    # 5 - Scan trades to create ownership array & value
    #   - Hold the number of shares currently owned (e.g. IBM has its own column)
    # 6 - Scan cash and value to create total fund value

    cash_history = []
    current_shares = np.zeros(len(symbols))
    share_ownership_history = []
    values_to_output = []

    for i in range(0, np.shape(adjusted_close_price)[0]):
        
        # Clear the hours and minutes from the adjusted prices - so that these match
        adjusted_close_price[i][len(symbols)] = adjusted_close_price[i][len(symbols)].replace(hour=0, minute=0)
        current_date = adjusted_close_price[i][len(symbols)]

        #print "Processing date " + str(current_date)
        
        for row in range (np.shape(traded_dates)[0]):
            trade = traded_dates[row,:]
            
            if trade[0] == current_date:

                # 4 - Scan trades to update cash
                days_prices = adjusted_close_price[i]
                stock = trade[1]
                volume = trade[2]
                #print "Trading " + str(volume) + " " + symbols[stock] + "@" + str(days_prices[stock])
                cash = cash - (days_prices[stock] * volume)

                # 5 - Scan trades to create ownership array & value
                current_shares[stock] = current_shares[stock] + volume
            
        cash_history.append(cash)
        share_ownership_history.append(current_shares.copy())
        
        # 6 - Scan cash and value to create total fund value
        prices = np.array(adjusted_close_price[i][0:len(symbols)], dtype=np.float)
        prices[np.isnan(prices)] = 0
        current_fund_value = cash + (current_shares * prices).sum()
        values_to_output.append([current_date.year, current_date.month, current_date.day, int(current_fund_value)])

    with open(values_file, 'wb') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(values_to_output)
