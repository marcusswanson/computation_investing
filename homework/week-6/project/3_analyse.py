#############################################
# Market simulation as detailed within
#
# http://wiki.quantsoftware.org/index.php?title=CompInvesti_Homework_4
#
# python 3_analyse.py values.csv $SPX
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
import matplotlib.pyplot as plt

def analyse(portfolio_value):
    
    # Work out the start and end periods - these are the start and end points of the imported data
    dates = portfolio_value[:,0]
    startdate = dates[0]
    enddate = dates[len(dates) - 1]
    
    # Add a day to the end date to match the incoming file
    startdate = startdate + dt.timedelta(hours=16)
    enddate = enddate + dt.timedelta(hours=16)

    print "Analysing period start:" + str(startdate)
    print "Until period end:" + str(enddate)

    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)

    c_benchmark_dataobj = da.DataAccess('Yahoo')
    ls_benchmark_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_benchmark_data = c_benchmark_dataobj.get_data(ldt_timestamps, [benchmark_stock], ls_benchmark_keys)
    d_benchmark_data = dict(zip(ls_benchmark_keys, ldf_benchmark_data))

    portfolio_data = np.array(portfolio_value[:,1])
    portfolio_data = portfolio_data.reshape((portfolio_data.size, 1))
    
    benchmark_data = d_benchmark_data['close'].values

    na_normalized_portfolio = portfolio_data / portfolio_data[0, :]
    na_normalized_benchmark = benchmark_data / benchmark_data[0, :]

    # Calculate the daily returns
    portfolio_daily_returns = portfolio_data.copy()
    tsu.returnize0(portfolio_daily_returns)

    benchmark_daily_returns = benchmark_data.copy()
    tsu.returnize0(benchmark_daily_returns)

    # Calculate the volatility
    portfolio_volatility = np.std(portfolio_daily_returns)
    benchmark_volatility = np.std(benchmark_daily_returns)
    
    # Calculate the average daily return
    portfolio_average_daily_return = np.mean(portfolio_daily_returns)
    benchmark_average_daily_return = np.mean(benchmark_daily_returns)
   
    # Sharpe Ratio is reward/risk
    # k * mean(daily_returns)/stdev(daily_returns)
    # k = sqrt(number_of_trading days)
    k = math.sqrt(252)
   
    portfolio_sharpe_ratio = k * portfolio_average_daily_return / portfolio_volatility
    benchmark_sharpe_ratio = k * benchmark_average_daily_return / benchmark_volatility

    # Calculate the normalized cumulative return
    portfolio_cum_ret = na_normalized_portfolio[na_normalized_portfolio.size - 1][0]
    benchmark_cum_ret = na_normalized_benchmark[na_normalized_benchmark.size - 1][0]

    # Plot the data
    initial_cash = portfolio_data[0]
    plotData = np.concatenate((na_normalized_benchmark * initial_cash, na_normalized_portfolio * initial_cash), axis = 1)
    plt.clf()
    plt.plot(ldt_timestamps, plotData)
    plt.legend([benchmark_stock,'Portfolio'])
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig('portfolioComparison.pdf', format='pdf')
    
    return (portfolio_volatility, benchmark_volatility, portfolio_average_daily_return, benchmark_average_daily_return, portfolio_sharpe_ratio, benchmark_sharpe_ratio, portfolio_cum_ret, benchmark_cum_ret);


if __name__ == '__main__':
    
    values_file = sys.argv[1]
    benchmark_stock = sys.argv[2]
    
    print 'Using values file:', values_file
    print 'Against benchmark stock:', benchmark_stock
    
    with open(values_file, 'r') as f:
        reader = csv.reader(f)
        csv_values = list(reader)

    portfolio_value = []

    for i in range(0, np.shape(csv_values)[0]):
        
        i_year = int(csv_values[i][0].strip())
        i_month = int(csv_values[i][1].strip())
        i_day = int(csv_values[i][2].strip())
        dt_trade_date = dt.datetime(i_year, i_month, i_day)
        f_amount = float(csv_values[i][3].strip())
        portfolio_value.append([dt_trade_date, f_amount])

    portfolio_value.sort(key=lambda day: day[0])
    portfolio_value = np.array(portfolio_value)

    p_vol, b_vol, p_daily_ret, b_daily_ret, p_sharpe, b_sharpe, p_cum_ret, b_cum_ret = analyse(portfolio_value)

    print "Sharpe Ratio of Fund: " + str(p_sharpe)
    print "Sharpe Ratio of " + benchmark_stock + ": " + str(b_sharpe)
    
    print "Volatility (stdev of daily returns) of Fund: " + str(p_vol)
    print "Volatility (stdev of daily returns) of " + benchmark_stock + ": " + str(b_vol)
    
    print "Average Daily Return of Fund: " + str(p_daily_ret)
    print "Average Daily Return of " + benchmark_stock + ": " + str(b_daily_ret)
    
    print "Cumulative Return of Fund: " + str(p_cum_ret)
    print "Cumulative Return of " + benchmark_stock + ": " + str(b_cum_ret)



