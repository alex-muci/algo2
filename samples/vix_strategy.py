#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import pandas as pd
import datetime as dt
import pandas_datareader.data as web  # then use df = web.DataReader(stocks, 'yahoo',start,end)

from algo2.utilities import range

from algo2 import utilities, statistics
from algo2.utilities import queue
from algo2.feeds.csv_files import HistoricCSVBarDataHandler

from algo2.strategies.buy_and_hold import BuyAndHoldStrategy

from algo2.pos_sizers.naive import AllInStockPositionSizer  # All in
from algo2.pos_refiners.naive import NaivePositionRefiner
from algo2.portfolio_handler import PortfolioHandler
from algo2.brokers.simulated_broker import IBSimulatedExecutionHandler
from algo2.statistics.simple import SimpleStatistics
from algo2.backtest import Backtest


def get_merged_data(config, ticker, all_in_fee, testing):
    """
    Read:
     - historical data from .csv (i.e. theoretical values for a security), and
     - new data from Yahoo (traded 'Adj Close' of a security)
    then rebase historical data and merge it with the new one
    to form a continuous daily Adj Close for backtesting purposes.
    :param config:  (e.g. utilities.DEFAULT) for default directories
    :param ticker: single ticker
    :param all_in_fee: estimated annual fee to be sutracted from theoretical values
    :param testing
    :return: dataframe of combined data (theoretical and new)
    """
    df_new, df_old = {}, {}
    # 1. download new data # and drop unwanted columns (keep only 'Adj Close')
    try:
        _start, _end = dt.datetime(1900, 1, 1), dt.date.today()
        df_new = web.DataReader(ticker.upper(), 'yahoo', _start, _end)
        # df_new.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)
    except IOError:
        print("No dataset, failing to download data from Yahoo")

    # 2. read old data (theo values), re-base it and merge with new
    f_in = os.path.join(config.CSV_DATA_DIR, "%s.csv" % ticker)
    df_old = pd.read_csv(f_in, header=0, parse_dates=True,
                         index_col=0, dayfirst=True, names=("Date", "Adj Close")
                         )  # note: dayFirst=True for format issues (European vs. American)

    # NB: assuming overlapping, i.e.  new_startdate > old_startdate
    old_lastdate = df_old.index.max()
    new_startdate = df_new.index.min()
    if new_startdate > old_lastdate:
        raise IOError("start_date of the new data later than old data last_date")

    # get theoretical data net of fees, if any:
    if all_in_fee != 0.0:
        perc = df_old["Adj Close"] / df_old["Adj Close"].shift(1) - 1 - all_in_fee / 365.0
        df_old['Adj Close net'] = df_old['Adj Close']
        start_pos_ = df_old.index.searchsorted(new_startdate)
        for i in range(start_pos_):
            df_old['Adj Close net'].iloc[i + 1] = df_old['Adj Close net'].iloc[i] \
                                                  * (1 + perc.iloc[i + 1])
        df_old['Adj Close'] = df_old['Adj Close net']  # rename & drop
        df_old.drop("Adj Close net", axis=1, inplace=True)

    # rebase
    mult = df_new.loc[new_startdate, "Adj Close"] \
        / df_old.loc[new_startdate, "Adj Close"]  # for rebasing
    df_old["Adj Close"] = df_old["Adj Close"] * mult

    # for consistency with rest of the file
    columns = ["Open", "High", "Low", "Close"]
    for cols in columns:
        df_old[cols] = df_old["Adj Close"]
    df_old["Volume"] = df_new["Volume"].loc[new_startdate]

    # return merged data and, if requested, save it
    start_pos = df_old.index.searchsorted(new_startdate)
    df_combo = pd.concat([df_old.iloc[:start_pos], df_new])
    if not testing:
        fout = config.OUTPUT_DIR + "/%s.csv" % ticker
        df_combo.to_csv(fout)

        # return df_combo  # ["Adj Close"]


def run(config, testing, tickers, filename, all_in_fee):
    # ##############################################
    #   GETTING (new, besides old saved) DATA, if not testing
    if not testing:
        for ticker in tickers:
            get_merged_data(config, ticker, all_in_fee, testing)
        csv_dir = config.OUTPUT_DIR
    else:
        csv_dir = config.CSV_DATA_DIR

    # ##############################################
    #   USUAL SET-UP
    # Set up variables for backtest()
    events_queue = queue.Queue()
    # csv_dir = config.CSV_DATA_DIR
    initial_equity = 500000.00

    # Use historic (Yahoo Daily) data handler
    data_handler = HistoricCSVBarDataHandler(csv_dir, events_queue, tickers)

    # Use the Buy-and-Hold Strategy
    strategy = BuyAndHoldStrategy(tickers, events_queue)
    # strategy = Strategies(strategy, DisplayStrategy())    # UN-COMMENT

    # Use an example Position Sizer and Refiner (risk mgt)
    position_sizer = AllInStockPositionSizer()  # i.e. All-in
    position_refiner = NaivePositionRefiner()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        initial_equity, events_queue, data_handler,
        position_sizer, position_refiner
    )

    # Use a simulated IB Execution Handler
    broker_handler = IBSimulatedExecutionHandler(events_queue, data_handler)  # , compliance)

    # Use the default Statistics
    stats = SimpleStatistics(config, portfolio_handler)

    # Set up the backtest
    backtest = Backtest(
        data_handler, strategy,
        portfolio_handler, broker_handler,
        position_sizer, position_refiner,
        stats, initial_equity
    )
    results = backtest.simulate_trading(testing=testing)
    statistics.save(filename, False)  # if True: also saves a .csv file with main curves
    return results


##############################################
def main():
    config = utilities.DEFAULT
    testing = False
    tickers = ['XIV']  # ['XIV', 'VXX']  # ; tickers = tickers.split(",")
    filename = ""
    run(config, testing, tickers, filename, 0.0)  # 0.024)


##############################################
if __name__ == "__main__":
    main()
