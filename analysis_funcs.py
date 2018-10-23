import numpy as np
import pandas as pd

# Compute moving averages across a defined window. Used to compute regimes
# INTERPRETATION: The regime is the short MAV minus the long MAV. A positive value indicates
# a bullish trend, so we want to buy as soon as the regime turns positive.
# Therefore, we want to identify in our data window points where the regime
# transitions from negative to positive (to buy) or from positive to negative (to sell)
def compute_mav_regime(short_interval, long_interval, data):
    # Labels for new columns
    short_label = "%sd_mav" % (str(short_interval))
    long_label = "%sd_mav" % (str(long_interval))

    # Compute the moving averages
    data[short_label] = np.round(data["Close"].rolling(window = short_interval, center = False).mean(), 2)
    data[long_label] = np.round(data["Close"].rolling(window = long_interval, center = False).mean(), 2)

    # Filter out the empty filler data (i.e. data for days needed to compute MAV_0 
    # but which itself does not have a MAV value calculated for it)
    data = data.dropna(how = "any")

    regime = (data[short_label] - data[long_label] > 0).apply(lambda x: 1 if x==True else -1)

    return regime 
    
    # regime = data[short_label] - data[long_label] > 0
    # regime = regime.apply(lambda x: 1 if x==True else -1)

    # return regime

# Compute gain/loss days and use to calculate on-balance volume (OBV)
# INTERPRETATION: OBV correlates volume to the stock's ability to appreciate on a day-to-day basis.
# therefore, if we see that OBV is rising and price is not, it's a good time to buy because the rising
# OBV suggests that price is soon to follow. 
# Therefore, we want a way to compare OBV and price (maybe MAV?). The higher OBV/MAV, the stronger
# the buy signal is. As that value decreases we will know to sell
def compute_obv(data):
    indicator_col = (data["Close"] - data["Open"] > 0).apply(lambda x: 1 if x==True else -1)
    obv_col = (data["Volume"]*indicator_col).cumsum() 
    return obv_col

# Compute moving average convergence-divergence (MACD) as a difference of exponential moving averages
# and also compute signal line, report both signals (MACD sign, as well as MACD against signal line)
# INTERPRETATION: Same as regime, simply using a different scheme of averages
# TODO - Fix these calculations - the EWM return type does not allow for series subtraction
def compute_macd(data):
    exp_26 = np.round(data["Close"].ewm(span = 26).mean(), 2)
    exp_12 = np.round(data["Close"].ewm(span = 12).mean(), 2)
    macd = (exp_12 - exp_26 > 0).apply(lambda x: 1 if x==True else -1)
    macd_signal = (macd - macd.ewm(span = 9).mean() > 0).apply(lambda x: 1 if x==True else -1)
    return macd_signal


################################################
################################################
# TODO: Insert method to do RSI calculations
# See http://www.investopedia.com/terms/r/rsi.asp
################################################
################################################


def pandas_candlestick_ohlc(dat, stick = "day", otherseries = None):
    """
    :param dat: pandas DataFrame object with datetime64 index, and float columns "Open", "High", "Low", and "Close", likely created via DataReader from "yahoo"
    :param stick: A string or number indicating the period of time covered by a single candlestick. Valid string inputs include "day", "week", "month", and "year", ("day" default), and any numeric input indicates the number of trading days included in a period
    :param otherseries: An iterable that will be coerced into a list, containing the columns of dat that hold other series to be plotted as lines
 
    This will show a Japanese candlestick plot for stock data stored in dat, also plotting other series if passed.
    """
    mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    alldays = DayLocator()              # minor ticks on the days
    dayFormatter = DateFormatter('%d')      # e.g., 12
 
    # Create a new DataFrame which includes OHLC data for each period specified by stick input
    transdat = dat.loc[:,["Open", "High", "Low", "Close"]]
    if (type(stick) == str):
        if stick == "day":
            plotdat = transdat
            stick = 1 # Used for plotting
        elif stick in ["week", "month", "year"]:
            if stick == "week":
                transdat["week"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[1]) # Identify weeks
            elif stick == "month":
                transdat["month"] = pd.to_datetime(transdat.index).map(lambda x: x.month) # Identify months
            transdat["year"] = pd.to_datetime(transdat.index).map(lambda x: x.isocalendar()[0]) # Identify years
            grouped = transdat.groupby(list(set(["year",stick]))) # Group by year and other appropriate variable
            plotdat = pd.DataFrame({"Open": [], "High": [], "Low": [], "Close": []}) # Create empty data frame containing what will be plotted
            for name, group in grouped:
                plotdat = plotdat.append(pd.DataFrame({"Open": group.iloc[0,0],
                                            "High": max(group.High),
                                            "Low": min(group.Low),
                                            "Close": group.iloc[-1,3]},
                                           index = [group.index[0]]))
            if stick == "week": stick = 5
            elif stick == "month": stick = 30
            elif stick == "year": stick = 365
 
    elif (type(stick) == int and stick >= 1):
        transdat["stick"] = [np.floor(i / stick) for i in range(len(transdat.index))]
        grouped = transdat.groupby("stick")
        plotdat = pd.DataFrame({"Open": [], "High": [], "Low": [], "Close": []}) # Create empty data frame containing what will be plotted
        for name, group in grouped:
            plotdat = plotdat.append(pd.DataFrame({"Open": group.iloc[0,0],
                                        "High": max(group.High),
                                        "Low": min(group.Low),
                                        "Close": group.iloc[-1,3]},
                                       index = [group.index[0]]))
 
    else:
        raise ValueError('Valid inputs to argument "stick" include the strings "day", "week", "month", "year", or a positive integer')
 
 
    # Set plot parameters, including the axis object ax used for plotting
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)
    if plotdat.index[-1] - plotdat.index[0] < pd.Timedelta('730 days'):
        weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
        ax.xaxis.set_major_locator(mondays)
        ax.xaxis.set_minor_locator(alldays)
    else:
        weekFormatter = DateFormatter('%b %d, %Y')
    ax.xaxis.set_major_formatter(weekFormatter)
 
    ax.grid(True)
 
    # Create the candelstick chart
    candlestick_ohlc(ax, list(zip(list(date2num(plotdat.index.tolist())), plotdat["Open"].tolist(), plotdat["High"].tolist(),
                      plotdat["Low"].tolist(), plotdat["Close"].tolist())),
                      colorup = "black", colordown = "red", width = stick * .4)
 
    # Plot other series (such as moving averages) as lines
    if otherseries != None:
        if type(otherseries) != list:
            otherseries = [otherseries]
        dat.loc[:,otherseries].plot(ax = ax, lw = 1.3, grid = True)
 
    ax.xaxis_date()
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
 
    plt.show()


