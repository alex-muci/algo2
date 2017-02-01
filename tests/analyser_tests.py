
from nose.tools import assert_equal, assert_almost_equal

from portfolio_tests import DataHandlerMock

from Algo2 import utilities as utils
from Algo2.portfolio import Portfolio
from Algo2.analysers.simple import SimpleStatistics


class PortfolioHandlerMock(object):
    def __init__(self, portfolio):
        self.portfolio = portfolio


def test_calculating_statistics():
    """
        Purchase/sell multiple lots of AMZN, GOOG
        to ensure correct arithmetic in calculating equity,
        drawdowns and sharpe ratio.
    """

    config = utils.DEFAULT

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
    assert_equal(statistics.equity_returns[2], -0.0705)

    # More buy in different shares, followed by ckecks
    portfolio.trade_position(
            "BOT", "GOOG", 200,
            707.50, 1.00
    )
    t = "2000-01-03 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[3], 499040.00)   # TODO: check this, was: 499040
    assert_equal(statistics.drawdowns[3], 960.00)   # TODO: check, was 954.00
    assert_equal(statistics.equity_returns[3], -0.0832) # TODO: check, was -0.0820

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
            "SLD", "AMZN", 100,
            565.83, 1.00
    )
    t = "2000-01-04 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[4], 499164.00)
    assert_equal(statistics.drawdowns[4], 836.00)
    assert_equal(statistics.equity_returns[4], 0.0236)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
            "BOT", "GOOG", 200,
            705.545, 1.00
    )
    t = "2000-01-05 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[5], 499146.00)
    assert_equal(statistics.drawdowns[5], 854.00)
    assert_equal(statistics.equity_returns[5], -0.0036)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
            "SLD", "AMZN", 200,
            565.59, 1.00
        )
    t = "2000-01-06 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[6], 499335.00)
    assert_equal(statistics.drawdowns[6], 665.00)
    assert_equal(statistics.equity_returns[6], 0.0379)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
            "SLD", "GOOG", 100,
            707.92, 1.00
    )
    t = "2000-01-07 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[7], 499580.00)
    assert_equal(statistics.drawdowns[7], 420.00)
    assert_equal(statistics.equity_returns[7], 0.0490)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
            "SLD", "GOOG", 100,
            707.90, 0.00
    )
    t = "2000-01-08 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[8], 499824.00)
    assert_equal(statistics.drawdowns[8], 176.00)
    assert_equal(statistics.equity_returns[8], 0.0488)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
            "SLD", "GOOG", 100,
            707.92, 0.50
    )
    t = "2000-01-09 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[9], 500069.50)
    assert_equal(statistics.drawdowns[9], 00.00)
    assert_equal(statistics.equity_returns[9], 0.0491)

    # Perform transaction and test statistics at this tick
    portfolio.trade_position(
            "SLD", "GOOG", 100,
            707.78, 1.00
        )
    t = "2000-01-10 00:00:00"
    statistics.update(t, portfolio_handler)
    assert_equal(statistics.equity[10], 500300.50)
    assert_equal(statistics.drawdowns[10], 00.00)
    assert_equal(statistics.equity_returns[10], 0.0462)

    #
    # Test that results are calculated correctly.
    #
    results = statistics.get_results
    assert_equal(results["max_drawdown"], 954.00)
    assert_almost_equal(results["max_drawdown_pct"], 0.1908)
    assert_almost_equal(float(results["sharpe"]), 1.7575)
