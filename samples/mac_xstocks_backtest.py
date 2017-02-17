#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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


def run(config, testing, tickers, filename, sw=100, lw=400):

    # ####################################
    # get the data via quandl for two vol ETFs: VXX (long vol) and XIV (short vol)
    # and merge


    # Set up variables needed for backtest
    events_queue = queue.Queue()
    csv_dir = config.CSV_DATA_DIR
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
    statistics.save(filename, False)    # if True: also saves a .csv file with main curves
    return results


##############################################
def main():
    config = utilities.DEFAULT
    testing = False
    tickers = ['SP500TR']  # ; tickers = tickers.split(",")
    filename = ""
    run(config, testing, tickers, filename)


##############################################
if __name__ == "__main__":
    main()
