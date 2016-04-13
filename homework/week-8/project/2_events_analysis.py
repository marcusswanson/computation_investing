#############################################
# Events analysis as detailed within
#
# http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_6
# http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_7
#
#
# python 2_events_analysis.py
#
#############################################

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import csv

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def find_events(df_data, ldt_timestamps, ls_symbols, s_market_symbol):
    ''' Finding the event dataframe '''
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_data)
    df_events = df_events * np.NAN
    ts_market = df_data[s_market_symbol]

    for s_sym in ls_symbols:
        print "Generating events for:" + s_sym
        
#        if s_market_symbol == s_sym:
#            print "Skipping:" + s_sym
#            continue
        
        for i in range(1, len(ldt_timestamps)):
            
            # Calculating the returns for this timestamp
            f_sym_bolval_today = df_data[s_sym].ix[ldt_timestamps[i]]
            f_sym_bolval_yest = df_data[s_sym].ix[ldt_timestamps[i - 1]]

            f_market_bolval_today = ts_market.ix[ldt_timestamps[i]]
            f_market_bolval_yest = ts_market.ix[ldt_timestamps[i - 1]]

            # Event is found if for the symbol:
            #
            #  Bollinger value for the equity today <= -2.0
            #  Bollinger value for the equity yesterday >= -2.0
            #  Bollinger value for SPY today >= 1.0

            if f_sym_bolval_today <= -2.0 and f_sym_bolval_yest >= -2.0 and f_market_bolval_today >= 1.0:
                print "Event:" + s_sym + "@" + str(ldt_timestamps[i])
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return (df_events, ldt_timestamps)

def generate_transactions_from_events(df_events, ldt_timestamps):

    values_to_output = []
    
    for s_sym in ls_symbols:
        print "Generating transactions for:" + s_sym
        for i in range(1, len(ldt_timestamps)):
            if df_events[s_sym].ix[ldt_timestamps[i]] == 1:

                buy_date = ldt_timestamps[i]
                # Output the BUY
                values_to_output.append([buy_date.year, buy_date.month, buy_date.day, s_sym, "BUY", 100])
                
                # Output the SELL
                sell_idx = i + 5
                if sell_idx < len(ldt_timestamps):
                    sell_date = ldt_timestamps[sell_idx]
                    values_to_output.append([sell_date.year, sell_date.month, sell_date.day, s_sym, "SELL", 100])

    with open("orders.csv", 'wb') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(values_to_output)

                
    return


if __name__ == '__main__':
    
    values_file = 'bollingerValues.csv'
    print 'Using values file:', values_file
    
    with open(values_file, 'r') as f:
        reader = csv.reader(f)
        csv_values = list(reader)

    np_imported_data = np.array(csv_values)

    np_bollinger = np_imported_data[1:,3:].astype(np.float)
    np_dates = np_imported_data[1:,0:3]
    ls_symbols = list(np_imported_data[0,3:])

    ##print "Bolling Values:" + str(np_bollinger)
    ##print "Dates:" + str(np_dates)
    ##print "Symbols:" + str(ls_symbols)

    ## Convert the dates into a list of timestamps
    ldt_timestamps = []
    for i in range(0, len(np_dates)):
        i_year = int(np_dates[i][0].strip())
        i_month = int(np_dates[i][1].strip())
        i_day = int(np_dates[i][2].strip())
        dt_trade_date = dt.datetime(i_year, i_month, i_day)
        ldt_timestamps.append(dt_trade_date)

    df_bollinger_data = pd.DataFrame(data=list(np_bollinger),index=ldt_timestamps,columns=ls_symbols)
    df_events, ldt_timestamps = find_events(df_bollinger_data, ldt_timestamps, ls_symbols, 'SPY')

    # Generate the buy/sell signals
    generate_transactions_from_events(df_events, ldt_timestamps)

    # Now we have found the events, perform an analysis on them
    dt_start = ldt_timestamps[0]
    dt_end = ldt_timestamps[len(ldt_timestamps) - 1]

    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='eventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
