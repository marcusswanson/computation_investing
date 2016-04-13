#############################################
# Events analysis as detailed within
#
# http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_4
#
#
# python 1_events_analysis.py
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


def find_events(ls_symbols, d_data, f_threshold):
    ''' Finding the event dataframe '''
    df_actual_close = d_data['actual_close']
    #df_high = d_data['high']
    
    ts_market = df_actual_close['SPY']

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_actual_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_actual_close.index

    for s_sym in ls_symbols:
        print "Generating events for:" + s_sym
        for i in range(1, len(ldt_timestamps)):
            
            # Calculating the returns for this timestamp
            f_symprice_today = df_actual_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_actual_close[s_sym].ix[ldt_timestamps[i - 1]]

            #week_ago_idx = i - 5
            #if week_ago_idx >= 0:
            #    f_symprice_today = df_actual_close[s_sym].ix[ldt_timestamps[i]]
            #    f_symprice_yest = df_actual_close[s_sym].ix[ldt_timestamps[i - 1]]
            
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]

            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the symbol was less than the threshold today
            # but greater/equal to the threshold yesterday
            if f_symprice_today < f_threshold and f_symprice_yest >= f_threshold:
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
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    f_threshold = 5.0

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events, ldt_timestamps = find_events(ls_symbols, d_data, f_threshold)

    generate_transactions_from_events(df_events, ldt_timestamps)
    
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='eventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
