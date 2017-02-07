"""
Test examples
One example can be test individually using:
$ nosetests -s -v tests/test_samples.py:test_strategy_backtest

"""
# TODO: add missing sample tests

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import os
from nose.tools import assert_equal, assert_almost_equal

from algo2 import utilities
from algo2.statistics.base_statistics import load
import samples.buy_and_hold_backtest
import samples.mac_xstocks_backtest


# Explicit access to module level variables:
# (like 'self' for the current module instead of the current instance)
this = sys.modules[__name__]                 # 'this' is a pointer to the module object instance it
this.config = utilities.DEFAULT              # then explicit assignment on it
this.testing = True                          # " "   " "     " "     " "
this.out_dir = utilities.DEFAULT.OUTPUT_DIR  # " "   " "     " "     " "


###################################
def test_buy_and_hold_backtest():
    """
    Test buy_and_hold
    Bar 0, at 2010-01-04 00:00:00
    Bar 1628, at 2016-06-22 00:00:00
    """
    tickers = ["SP500TR"]
    filename = os.path.expanduser(os.path.join(this.out_dir, "buy_and_hold_backtest.pkl"))
    results = samples.buy_and_hold_backtest.run(this.config, this.testing, tickers, filename)

    for (key, expected) in [
        ('sharpe', 0.6408),
        ('max_drawdown_pct', 5.0308),
        ('max_drawdown', 30174.0112)
    ]:
        value = float(results[key])
        assert_almost_equal(value, expected, places=4)

    for (key, expected) in [
            ('equity_returns', {'min': -1.5775, 'max': 1.2712, 'first': 0.0000, 'last': -0.0579}),
            ('drawdowns', {'min': 0.0, 'max': 30174.011, 'first': 0.0, 'last': 4537.01}),
            ('equity', {'min': 488958.003, 'max': 599782.008, 'first': 500000.0, 'last': 595245})
    ]:
        values = results[key]
        assert_almost_equal(float(min(values)), expected['min'], places=3)
        assert_almost_equal(float(max(values)), expected['max'], places=3)
        assert_almost_equal(float(values.iloc[0]), expected['first'], places=2)
        assert_almost_equal(float(values.iloc[-1]), expected['last'], places=2)

    # test save and load (pickle)
    stats = load(filename)
    results = stats.get_results()
    assert_almost_equal(float(results['sharpe']), 0.6408)
    assert_almost_equal(float(results['max_drawdown_pct']), 5.0308)


###################################
def test_mac_backtest():
    """
    Test mac_backtest
    """
    tickers = ["SP500TR"]
    filename = os.path.expanduser(os.path.join(this.out_dir, "mac_backtest.pkl"))
    results = samples.mac_xstocks_backtest.run(this.config, this.testing, tickers, filename)

    assert_almost_equal(float(results['sharpe']), 0.6388, places=2)
    assert_almost_equal(float(results['max_drawdown_pct']), 4.4979, places=2)
