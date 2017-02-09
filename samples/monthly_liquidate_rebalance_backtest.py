#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime

from algo2 import utilities
from algo2.utilities import queue
from algo2.feeds.csv_files import HistoricCSVBarDataHandler

#   thi strategy needs the relevant position sizer
from algo2.strategies.monthly_liquidate_rebalance_strategy import MonthlyLiquidateRebalanceStrategy
from algo2.pos_sizers.rebalance import LiquidateRebalancePositionSizer

from algo2.pos_refiners.naive import NaivePositionRefiner
from algo2.portfolio_handler import PortfolioHandler
from algo2.brokers.simulated_broker import IBSimulatedExecutionHandler
from algo2.statistics.simple import SimpleStatistics
from algo2.backtest import Backtest


def run(config, testing, tickers, filename):

    # Set up variables needed for backtest
    events_queue = queue.Queue()
    csv_dir = config.CSV_DATA_DIR
    initial_equity = 500000.00

    start_date = datetime.datetime(2006, 11, 1)
    end_date = datetime.datetime(2016, 10, 12)

    # Use historic data Handler,
    # with start date and end date
    data_handler = HistoricCSVBarDataHandler(
        csv_dir, events_queue, tickers,
        start_date=start_date, end_date=end_date
    )

    # Use the monthly liquidate and rebalance strategy
    strategy = MonthlyLiquidateRebalanceStrategy(tickers, events_queue)

    # Use the liquidate and rebalance position sizer
    # with pre-specified ticker weights
    ticker_weights = {
        "SPY": 0.6,
        "AGG": 0.4,
    }

    # Use relevant position sizer
    position_sizer = LiquidateRebalancePositionSizer(ticker_weights)
    position_refiner = NaivePositionRefiner()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        initial_equity, events_queue, data_handler,
        position_sizer, position_refiner
    )

    # Use a simulated IB Execution Handler
    broker = IBSimulatedExecutionHandler(
        events_queue, data_handler,
    )

    # Use the default Statistics
    statistics = SimpleStatistics(config, portfolio_handler)

    # Set up the backtest
    backtest = Backtest(
        data_handler, strategy,
        portfolio_handler, broker,
        position_sizer, position_refiner,
        statistics, initial_equity
    )
    results = backtest.simulate_trading(testing=testing)
    statistics.save(filename, False)    # if True: also saves a .csv file with main curves
    return results


##############################################
def main():
    config = utilities.DEFAULT
    testing = False
    tickers = ['SPY', 'AGG']
    filename = ""
    run(config, testing, tickers, filename)


##############################################
if __name__ == "__main__":
    main()
