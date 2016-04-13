#############################################
# Bollinger bands
#
# http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_5
#
# python bollinger_bands.py
#
#############################################

import pandas as pd
import numpy as np
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import matplotlib.pyplot as plt

def bollinger_bands(dt_startdate, dt_enddate, ls_symbols, i_num_of_days):
    
    print "Creating Bollinger Bands"
    print "Start Date:" + str(dt_startdate)
    print "End Date:" + str(dt_enddate)
    print "Symbols:" + str(ls_symbols)
    print "Rolling Period:" + str(i_num_of_days)
    
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_startdate, dt_enddate, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Extract the price, mean, upper and lower bands
    pricedat = np.array(d_data['close'].values)
    rolling_mean = pd.rolling_mean(pricedat, i_num_of_days)
    rolling_std = pd.rolling_std(pricedat, i_num_of_days)
    upper_band = rolling_mean + rolling_std
    lower_band = rolling_mean - rolling_std

    #  Calculate the bollinger values
    bollinger_value = (pricedat - rolling_mean) / (rolling_std)
    
    # Plot the values
    for i in range(0, np.shape(pricedat)[1]):
        
        plotData = np.concatenate((pricedat[:,i].reshape((pricedat[:,i].size, 1)),
                                   rolling_mean[:,i].reshape((rolling_mean[:,i].size, 1)),
                                   upper_band[:,i].reshape((upper_band[:,i].size, 1)),
                                   lower_band[:,i].reshape((lower_band[:,i].size, 1))), axis = 1)

        plt.clf()
        plt.plot(ldt_timestamps, plotData)
        plt.legend(['Price','Rolling Mean','Upper band', 'Lower Band'])
        plt.ylabel('Adjusted Close')
        plt.xlabel('Date')
        bollingerBandsFilename = str(ls_symbols[i]) + "-bollingerBands.pdf"
        plt.savefig(bollingerBandsFilename, format='pdf')

        plt.clf()
        plt.plot(ldt_timestamps, bollinger_value[:,i].reshape((bollinger_value[:,i].size, 1)))
        plt.ylabel('Bollinger Feature')
        plt.xlabel('Date')
        bollingerValuesFilename = str(ls_symbols[i]) + "-bollingerValues.pdf"
        plt.savefig(bollingerValuesFilename, format='pdf')

    return bollinger_value


if __name__ == '__main__':
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    bollingerValues = bollinger_bands(dt_start, dt_end, ['AAPL','GOOG','IBM','MSFT'], 20)
    print bollingerValues
    
