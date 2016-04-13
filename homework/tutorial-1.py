import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

print "start"

# Create the list of stocks we are interested in
ls_symbols = ["AAPL", "GLD", "GOOG", "$SPX", "XOM"]

# Creat the period we are interested in for those stocks
dt_start = dt.datetime(2006, 1, 1)
dt_end = dt.datetime(2010, 12, 31)
dt_timeofday = dt.timedelta(hours=16)

# Get the days that the New York Stock Exchange is open for those days
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

# Get the data from Yahoo, using the reference keys supplied below
c_dataobj = da.DataAccess('Yahoo')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

# Get the adjusted close prices which are different from the actual close prices
na_price = d_data['close'].values
plt.clf()
plt.plot(ldt_timestamps, na_price)
plt.legend(ls_symbols)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
plt.savefig('adjustedclose.pdf', format='pdf')

# Generate the normalised data

na_normalized_price = na_price / na_price[0, :]
plt.clf()
plt.plot(ldt_timestamps, na_normalized_price)
plt.legend(ls_symbols)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
plt.savefig('normalisedAdjustedClose.pdf', format='pdf')


# It is very often useful to look at the returns by day for individual stocks.
# The general equation for daily return on day t is:
#
#    ret(t) = (price(t)/price(t-1)) -1 
#
# We can compute this in Python all at once as using the builtin QSTK function returnize0:

na_rets = na_normalized_price.copy()
tsu.returnize0(na_rets)

plt.clf()
plt.plot(ldt_timestamps, na_rets)
plt.legend(ls_symbols)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
plt.savefig('returnsPerDay.pdf', format='pdf')


print "end"
