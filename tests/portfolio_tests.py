#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from nose.tools import assert_equal

from algo2.feeds.base_feed import AbstractTickDataHandler
from algo2.portfolio import Portfolio

# TODO: test Bar, but mainly Futures (besides stock positions)

# mock class to use in Portfolio __init__
class DataHandlerMock(AbstractTickDataHandler):
    # fnct below is to update position values
    def get_best_bid_ask(self, ticker):
        prices = {
            "GOOG": (705.4, 705.46),
            "AMZN": (564.14, 565.14),
        }
        return prices[ticker]

def test_Tick_stock_portfolio():
    """
    Test a portfolio consisting of Amazon and Google/Alphabet
    with various orders to create round-trips for both.

    These orders were carried out in the Interactive Brokers
    demo account and checked for cash, equity and PnL
    equality.
    """
    #   Set up the Portfolio object
    dh = DataHandlerMock()
    cash = 500000.00 # 0.5 mln
    portfolio = Portfolio(dh, cash)

    # 1. Buy 300 of AMZN over two transactions
    portfolio.trade_position(
            "BOT", "AMZN", 100,
            566.56, 1.00
    )
    portfolio.trade_position(
            "BOT", "AMZN", 200,
            566.395, 1.00
    )
    # 2. Buy 200 GOOG
    portfolio.trade_position(
            "BOT", "GOOG", 200,
            707.50, 1.00
    )
    # 3. Sell partly AMZN position by 100 shares
    portfolio.trade_position(
            "SLD", "AMZN", 100,
            565.83, 1.00
        )
    # 4. Add to the GOOG position by 200 shares
    portfolio.trade_position(
            "BOT", "GOOG", 200,
            705.545, 1.00
    )
    # 5. Sell 200 of the AMZN shares
    portfolio.trade_position(
            "SLD", "AMZN", 200,
            565.59, 1.00
    )
    # 6. Sell 300 GOOG from the portfolio in three steps
    portfolio.trade_position(
            "SLD", "GOOG", 100,
            704.92, 1.00
    )
    portfolio.trade_position(
            "SLD", "GOOG", 100,
            704.90, 0.0
    )
    portfolio.trade_position(
            "SLD", "GOOG", 100,
            704.92, 0.50
    )
    portfolio.trade_position(
            "SLD", "GOOG", 100,
            704.78, 1.00
    )

    # The figures below are derived from Interactive Brokers
    # demo account using the above trades with prices provided
    # by their demo feed.
    assert_equal(len(portfolio.positions), 0)           # no. open positions = 0
    assert_equal(len(portfolio.closed_positions), 2)    # no. closed positions
    assert_equal(portfolio.cur_cash, 499100.50)
    assert_equal(portfolio.equity, 499100.50)
    assert_equal(portfolio.unrealised_pnl, 0.00)
    assert_equal(portfolio.realised_pnl, -899.50)

#if __name__ == "__main__":
#    test_Tick_stock_portfolio()
#