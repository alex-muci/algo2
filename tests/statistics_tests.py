#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_equal, assert_almost_equal

# from decimal import Decimal
from portfolio_tests import DataHandlerMock

import algo2.utilities as utilities
from algo2.portfolio import Portfolio
from algo2.statistics.simple import SimpleStatistics


class PortfolioHandlerMock(object):
    def __init__(self, portfolio):
        self.portfolio = portfolio


def test_calculating_statistics():
    """
        Purchase/sell multiple lots of AMZN, GOOG
        to ensure correct arithmetic in calculating equity,
        drawdowns and sharpe ratio.
        Values checked in Excel (were wrong in QSTRADER)
    """

    config = utilities.DEFAULT  # for default dir of datafeed and output

    # Create Statistics object
    data_handler = DataHandlerMock()
    portfolio = Portfolio(data_handler, 500000.00)
    portfolio_handler = PortfolioHandlerMock(portfolio)
    statistics = SimpleStatistics(config, portfolio_handler)

    # Check initialization
    assert_equal(statistics.equity[0], 500000.00)
    assert_equal(statistics.drawdowns[0], 00)
    assert_equal(statistics.equity_returns[0], 0.0)

    # One buy trade, followed by ckecks
    portfolio.trade_position(
        "BOT", "AMZN", 100,
        566.56, 1.00
    )
    t = "2000-01-01 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[1], 499807.00)
    assert_equal(statistics.drawdowns[1], 193.00)
    assert_equal(statistics.equity_returns[1], -0.0386)

    # One more buy trade, followed by ckecks
    portfolio.trade_position(
        "BOT", "AMZN", 200,
        566.395, 1.00
    )
    t = "2000-01-02 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[2], 499455.00)
    assert_equal(statistics.drawdowns[2], 545.00)
    assert_equal(statistics.equity_returns[2], -0.0704)

    # More buy in different shares, followed by ckecks
    portfolio.trade_position(
        "BOT", "GOOG", 200,
        707.50, 1.00
    )
    t = "2000-01-03 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[3], 499040.00) 
    assert_equal(statistics.drawdowns[3], 960.00)  
    assert_equal(statistics.equity_returns[3], -0.0831)  

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
        "SLD", "AMZN", 100,
        565.83, 1.00
    )
    t = "2000-01-04 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[4], 499158.00)
    assert_equal(statistics.drawdowns[4], 842.00)
    assert_equal(statistics.equity_returns[4], 0.0236)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
        "BOT", "GOOG", 200,
        705.545, 1.00
    )
    t = "2000-01-05 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[5], 499134.00)
    assert_equal(statistics.drawdowns[5], 866.00)
    assert_equal(statistics.equity_returns[5], -0.0048)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
        "SLD", "AMZN", 200,
        565.59, 1.00
    )
    t = "2000-01-06 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[6], 499323.00)
    assert_equal(statistics.drawdowns[6], 677.00)
    assert_equal(statistics.equity_returns[6], 0.0379)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
        "SLD", "GOOG", 100,
        707.92, 1.00
    )
    t = "2000-01-07 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[7], 499571.00)
    assert_equal(statistics.drawdowns[7], 429.00)
    assert_equal(statistics.equity_returns[7], 0.0497)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
        "SLD", "GOOG", 100,
        707.90, 0.00
    )
    t = "2000-01-08 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[8], 499818.00)
    assert_equal(statistics.drawdowns[8], 182.00)
    assert_equal(statistics.equity_returns[8], 0.0494)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
        "SLD", "GOOG", 100,
        707.92, 0.50
    )
    t = "2000-01-09 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[9], 500066.50)
    assert_equal(statistics.drawdowns[9], 00.00)
    assert_equal(statistics.equity_returns[9], 0.0497)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
        "SLD", "GOOG", 100,
        707.78, 1.00
    )
    t = "2000-01-10 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[10], 500300.50)
    assert_equal(statistics.drawdowns[10], 00.00)
    assert_equal(statistics.equity_returns[10], 0.0468)

    #
    # Test that results are calculated correctly.
    #
    results = statistics.get_results()
    assert_equal(results["max_drawdown"], 960.00)
    assert_almost_equal(results["max_drawdown_pct"], 0.192)  # (top - bottom) / top
    assert_almost_equal(float(results["sharpe"]), 1.7513)
    print("done")
