#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import numpy as np
import pandas as pd
import quandl
import datetime as dt
import pandas_datareader.data as web  # then use df = web.DataReader(stocks, 'yahoo',start,end)

from algo2 import utilities
from algo2.utilities import queue
from algo2.feeds.csv_files import HistoricCSVBarDataHandler

from algo2.strategies.moving_average_cross_xstocks import MovingAverageCrossStrategy

from algo2.pos_sizers.naive import FixedPositionSizer
from algo2.pos_refiners.naive import NaivePositionRefiner
from algo2.portfolio_handler import PortfolioHandler
from algo2.brokers.simulated_broker import IBSimulatedExecutionHandler
from algo2.statistics.simple import SimpleStatistics
from algo2.backtest import Backtest


def get_merged_data(config, ticker):
    """
    Read:
     - historical data from .csv (i.e. theoretical values for a security), and
     - new data from Yahoo (traded 'Adj Close' of a security)
    then rebase historical data and merge it with the new one
    to form a continuous daily Adj Close for backtesting purposes.
    :param config:  (e.g. utilities.DEFAULT) for default directories
    :param ticker: single ticker
    :return: dataframe of combined data (theoretical and new)
    """
    csv_dir = config.CSV_DATA_DIR
    df_new, df_old = {}, {}

    # 1. download new data
    try:
        _start, _end = dt.datetime(1900, 1, 1), dt.date.today()
        df_new = web.DataReader(ticker.upper(), 'yahoo', _start, _end)
    except IOError:
        print("No dataset, failing to download data from Yahoo")

    # 2. read old data (theo values), re-base it and merge with new
    f_in = os.path.join(csv_dir, "%s.csv" % ticker)
    df_old = pd.read_csv(f_in, header=0, parse_dates=True,
                         index_col=0, dayfirst=True, names=("Date", "Adj Close")
                         )  # note: dayFirst=True for format issues (European vs. American)

    # get date where to merge and find the multiplier
    # NB: assuming overlapping, i.e.  new_startdate > old_startdate
    old_lastdate = df_old.index.max()
    new_startdate = df_new.index.min()
    if new_startdate > old_lastdate:
        raise IOError("start_date of the new data later than old data last_date")
    else:
        mult = df_new[new_startdate]["Adj Close"] \
                / df_old[new_startdate]["Adj Close"]  # for rebasing

    df_old["Adj Close"] = df_old["Adj Close"] * mult

    # fill old prices (containing only Adj Close) with other cols (Open, High, ...)
    for col_name in ["Open", "High", "Low", "Close"]:
        df_old[col_name] = df_old["Adj Close"]
    df_old["Volume"] = np.nan
    # df_old.drop(colname, axis=1, inplace=True)

    # save merged data and return df
    df_combo = pd.concat([df_old.loc[:new_startdate], df_new])
    fout = config.OUTPUT_DIR + "/combo_%s.csv" % ticker  # tkr.replace("/", "-")
    df_combo.to_csv(fout)
    return df_combo

"""
def run(config, testing, tickers, filename, sw=100, lw=400):
    csv_dir = config.CSV_DATA_DIR
    # ##############################################
    #   GETTING DATA if not testing
    if not testing:
        # quandl: CHANGE TO YOUR DIRECTORY
        api_key = open('C:/Users/Alessandro/quandlapikey.txt', 'r').read()
        quandl.ApiConfig.api_key = api_key  # = "YOUR_KEY_HERE"

        df_new, df_old = {}, {}
        for tkr in tickers:
            # 1. download new data
            try:
                full_tkr = "YAHOO/%s" % tkr.upper()
                df_new[tkr] = quandl.get(full_tkr, returns="pandas", authtoken=api_key)  # get the data
                df_new[tkr].rename(columns={'Adjusted Close': 'Adj Close'}, inplace=True)  # rename 1 column
            except quandl.NotFoundError:
                print("No dataset")
            # 2. read old data (theo values), re-base it and merge with new
            f_in = os.path.join(csv_dir, "%s.csv" % tkr)
            df_old[tkr] = pd.read_csv(f_in, header=0, parse_dates=True,
                                      index_col=0, dayfirst=True, names=("Date", "Adj Close")
                                      )  # note: dayFirst=True for format issues (European vs. American)

            fout = config.OUTPUT_DIR + "/combo_%s.csv" % tkr  # tkr.replace("/", "-")
            df_old[tkr].to_csv(fout)

            old_startdate = df_old[tkr].index.min()
            old_lastdate = df_old[tkr].index.max()
            new_startdate = df_new[tkr].index.min()  # Hp: overlapping, i.e.  new_startdate > old_startdate

            if new_startdate > old_lastdate:
                raise IOError("start_date of the new data later than old data last_date")
            else:
                mult = df_new[tkr][new_startdate]["Adj Close"] \
                      / df_old[tkr][new_startdate]["Adj Close"] # for rebasing

                columns = ["Open", "High", "Low", "Close"]
                for col_name in columns:
                    df_old[tkr][col_name] = df_old["Adj Close"]
                df_old["Volume"] = np.nan

                # df_old.drop('temp_values', axis=1, inplace=True)  # axis = 1 for cols, inplace for change to stay inplace

            # save merged data
            df_combo = pd.concat([df_old[:-100], df_new])
            fout = config.OUTPUT_DIR + "/combo_%s.csv" % tkr  # tkr.replace("/", "-")
            df_combo.to_csv(fout)

"""
"""

    # ##############################################
    #   USUAL SET-UP
    events_queue = queue.Queue()
    # csv_dir = config.CSV_DATA_DIR
    initial_equity = 500000.00

    # Use historic data Handler
    data_handler = HistoricCSVBarDataHandler(csv_dir, events_queue, tickers)

    # Use the MAC Strategy
    strategy = MovingAverageCrossStrategy(tickers, events_queue, sw, lw)

    # Use an example Position Sizer and Refiner (risk mgt)
    position_sizer = FixedPositionSizer()
    position_refiner = NaivePositionRefiner()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        initial_equity, events_queue, data_handler,
        position_sizer, position_refiner
    )

    # Use a simulated IB Execution Handler
    execution_handler = IBSimulatedExecutionHandler(events_queue, data_handler)

    # Use the default Statistics
    statistics = SimpleStatistics(config, portfolio_handler)

    # Set up the backtest
    backtest = Backtest(
        data_handler, strategy,
        portfolio_handler, execution_handler,
        position_sizer, position_refiner,
        statistics, initial_equity
    )
    results = backtest.simulate_trading(testing=testing)
    statistics.save(filename, False)  # if True: also saves a .csv file with main curves
    return results
"""


##############################################
def main():
    config = utilities.DEFAULT
    testing = False
    tickers = ['XIV']  # ['XIV', 'VXX']  # ; tickers = tickers.split(",")
    filename = ""
    get_merged_data(config, tickers)
    # run(config, testing, tickers, filename)


##############################################
if __name__ == "__main__":
    main()
