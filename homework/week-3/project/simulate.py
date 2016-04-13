#!/usr/bin/python
# Completing coursework from http://wiki.quantsoftware.org/index.php?title=CompInvestI_Homework_1

import math

import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Simulate function definition is here
def simulate( startdate, enddate, symbols, allocations ):
   "This simulates and assess the performance of a 4 stock portfolio"

   print "Start Date: " +  startdate.strftime('Start Date: %d, %b %Y')
   print "End Date: " + enddate.strftime('Start Date: %d, %b %Y')
   print "Symbols: " + str(symbols)
   print "Allocations:" + str(allocations)

   dt_timeofday = dt.timedelta(hours=16)

   # Get the days that the New York Stock Exchange is open for those days
   ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)

   # Get the data from Yahoo, using the reference keys supplied below
   c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
   ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
   ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
   d_data = dict(zip(ls_keys, ldf_data))

   # Read in adjusted closing prices for the 4 equities.
   pricedat = d_data['close'].values

   # It is very often useful to look at the returns by day for individual stocks.
   # The general equation for daily return on day t is:
   #
   #    ret(t) = (price(t)/price(t-1)) -1 
   #
   # We can compute this in Python all at once as using the builtin QSTK function returnize0:
   #daily_rets = na_normalized_price.copy()
   #tsu.returnize0(daily_rets)

   # Normalize the prices according to the first day.
   # The first row for each stock should have a value of 1.0 at this point.
   na_normalized_price = pricedat / pricedat[0, :]

   #print "Normalized Price"
   #print na_normalized_price[0:3, :]
   
   # Multiply each column by the allocation to the corresponding equity.
   na_allocated_normalized_price = na_normalized_price * allocations

   #print "Allocated Normalized Price"
   #print na_allocated_normalized_price[0:3, :]
   
   # Sum each row for each day. That is your cumulative daily portfolio value.
   cumulative_daily_portfolio_value = np.sum(na_allocated_normalized_price, axis = 1)

   #print "Cumulative Daily Portfolio Value"
   #print cumulative_daily_portfolio_value
   
   # Compute statistics from the total portfolio value. 
   daily_rets = cumulative_daily_portfolio_value.copy()
   tsu.returnize0(daily_rets)

   vol = np.std(daily_rets)
   average_daily_ret = np.mean(daily_rets)
   
   # Sharpe Ratio is reward/risk
   # k * mean(daily_returns)/stdev(daily_returns)
   # k = sqrt(number_of_trading days)
   k = math.sqrt(daily_rets.size) # This may need to be 252
   
   sharpe = k * average_daily_ret / vol
   
   cum_ret = cumulative_daily_portfolio_value[cumulative_daily_portfolio_value.size - 1]
   
   return (vol, average_daily_ret, sharpe, cum_ret);


# Optimize function definition is here
def optimize( startdate, enddate, symbols ):
   "This optimises the  and assess the performance of a 4 stock portfolio"

   print "Start Date: " +  startdate.strftime('Start Date: %d, %b %Y')
   print "End Date: " + enddate.strftime('Start Date: %d, %b %Y')
   print "Symbols: " + str(symbols)

   best_cum_ret = 0
   best_vol = 0
   best_daily_ret = 0
   best_sharpe = 0
   best_cum_ret = 0
   best_allocation = [0.0, 0.0, 0.0, 0.0]

   loopRange = np.arange(0,1.1,0.1)

   for allocOne in loopRange:
      for allocTwo in loopRange:
         for allocThree in loopRange:
            for allocFour in loopRange:
               if(allocOne + allocTwo + allocThree + allocFour) == 1.0:
                  print "========================================================"
                  allocation = [allocOne, allocTwo, allocThree, allocFour]

                  vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, symbols, allocation)

                  if sharpe > best_sharpe:
                     best_vol = vol
                     best_daily_ret = daily_ret
                     best_sharpe = sharpe
                     best_cum_ret = cum_ret
                     best_allocation = allocation

                  print "Sharpe Ratio: " + str(sharpe)
                  print "Volatility (stdev of daily returns): " + str(vol)
                  print "Average Daily Return: " + str(daily_ret)
                  print "Cumulative Return: " + str(cum_ret)
                  print "========================================================"

   print "Best Allocation: " + str(best_allocation)
   print "Best Sharpe Ratio: " + str(best_sharpe)
   print "Best Volatility (stdev of daily returns): " + str(best_vol)
   print "Best Average Daily Return: " + str(best_daily_ret)
   print "Best Cumulative Return: " + str(best_cum_ret)
   
   return (best_allocation);

##########################################################################
##########################################################################
##########################################################################

# Now you can call simulate function
print "============================Part 2.5============================"
startdate = dt.datetime(2011, 1, 1)
enddate = dt.datetime(2011, 12, 31)
dt.tzinfo
vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, ['AAPL', 'GLD', 'GOOG', 'XOM'], [0.4, 0.4, 0.0, 0.2])

print "Sharpe Ratio:: " + str(sharpe)
print "Volatility (stdev of daily returns): " + str(vol)
print "Average Daily Return: " + str(daily_ret)
print "Cumulative Return: " + str(cum_ret)

print "============================"

startdate = dt.datetime(2010, 1, 1)
enddate = dt.datetime(2010, 12, 31)

vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, ['AXP', 'HPQ', 'IBM', 'HNZ'], [0.0, 0.0, 0.0, 1.0])

print "Sharpe Ratio:: " + str(sharpe)
print "Volatility (stdev of daily returns): " + str(vol)
print "Average Daily Return: " + str(daily_ret)
print "Cumulative Return: " + str(cum_ret)
print "================================================================"

print "============================Part 3============================"

startdate = dt.datetime(2010, 1, 1)
enddate = dt.datetime(2010, 12, 31)
symbols = ['AAPL', 'GLD', 'GOOG', 'XOM']
optimized_allocation = optimize(startdate, enddate, symbols)

print "Best Allocation:" + str(optimized_allocation)

print "================================================================"

print "============================Part 4============================"

print "Simulating Optimised Allocation:" + str(optimized_allocation)

vol, daily_ret, sharpe, cum_ret = simulate(startdate, enddate, symbols, optimized_allocation)

print "Best Sharpe Ratio: " + str(sharpe)
print "Best Volatility (stdev of daily returns): " + str(vol)
print "Best Average Daily Return: " + str(daily_ret)
print "Best Cumulative Return: " + str(cum_ret)

# Compare the portfolio return against SPY

dt_timeofday = dt.timedelta(hours=16)
ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)
c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
ldf_benchmark_data = c_dataobj.get_data(ldt_timestamps, ['SPY'], ls_keys)
d_data = dict(zip(ls_keys, ldf_data))
d_benchmark_data = dict(zip(ls_keys, ldf_benchmark_data))

pricedat = d_data['close'].values
benchmarkdat = d_benchmark_data['close'].values

na_normalized_price = pricedat / pricedat[0, :]
na_normalized_benchmark = benchmarkdat / benchmarkdat[0, :]

na_allocated_normalized_price = na_normalized_price * optimized_allocation
cumulative_daily_portfolio_value = np.sum(na_allocated_normalized_price, axis = 1)

cumulative_daily_portfolio_value = cumulative_daily_portfolio_value.reshape((cumulative_daily_portfolio_value.size, 1))
plotData = np.concatenate((na_normalized_benchmark, cumulative_daily_portfolio_value), axis = 1)

plt.clf()
plt.plot(ldt_timestamps, plotData)
plt.legend(['SPY','MXS'])
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
plt.savefig('portfolioComparison.pdf', format='pdf')

print "================================================================"
