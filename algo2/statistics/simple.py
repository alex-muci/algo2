#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from algo2.statistics.base_statistics import AbstractStatistics
from algo2.utilities import pickle
import algo2.statistics.performance as perf


class SimpleStatistics(AbstractStatistics):
    """
    SimpleStatistics provides a bare-bones example of statistics
    that can be collected through trading.

    Statistics included are:
    - Sharpe Ratio,
    - Drawdown, Max Drawdown and Max Drawdown Duration.

    TODO think about Alpha/Beta, compare strategy of benchmark.
    TODO think about speed -- will be bad doing for every tick
    on anything that trades sub-minute.
    TODO think about slippage, fill rate, etc
    TODO brokerage costs?
    TODO need some kind of trading-frequency parameter in setup.
    Sharpe calculations need to know if daily, hourly, minutely, etc.
    """
    def __init__(self, config, portfolio_handler):
        """
        Takes in a portfolio handler.
        """
        self.config = config
        self.drawdowns = [0]
        self.equity = []
        self.equity_returns = [0.0]
        # Initialize timeseries. Correct timestamp not available yet.
        self.timeseries = ["0000-00-00 00:00:00"]
        # Initialize in order for first-step calculations to be correct.
        current_equity = portfolio_handler.portfolio.equity
        self.hwm = [current_equity]
        self.equity.append(current_equity)

    def update(self, timestamp, portfolio_handler):
        """
        Update all statistics that must be tracked over time.
        - time(stamp)series
        - equity
        and calculate equity_returns, hwm, drawdowns
        """
        if timestamp != self.timeseries[-1]:
            # Retrieve equity value of Portfolio, up
            current_equity = portfolio_handler.portfolio.equity
            self.equity.append(current_equity)  # update equity
            # append timestamp
            self.timeseries.append(timestamp)   # update time

            # Calculate percentage return between current and previous equity value.
            # ## NB: in 'QSTRADER' the denominator is self.equity[-1] ## #
            pct = (self.equity[-1] - self.equity[-2]) / self.equity[-2] * 100
            self.equity_returns.append(round(pct, 4))
            # Calculate drawdown
            self.hwm.append(max(self.hwm[-1], self.equity[-1]))
            self.drawdowns.append(self.hwm[-1] - self.equity[-1])

    def get_results(self):
        """
        Return a dict with all important results & stats.
        """

        # Modify timeseries in local scope only. We initialize with 0-date,
        # but would rather show a realistic starting date.
        timeseries = self.timeseries
        timeseries[0] = pd.to_datetime(timeseries[1]) - pd.Timedelta(days=1)

        statistics = {}
        statistics["sharpe"] = self._calculate_sharpe()
        statistics["drawdowns"] = pd.Series(self.drawdowns, index=timeseries)
        statistics["max_drawdown"] = max(self.drawdowns)
        statistics["max_drawdown_pct"] = self._calculate_max_drawdown_pct()
        statistics["equity"] = pd.Series(self.equity, index=timeseries)
        statistics["equity_returns"] = pd.Series(self.equity_returns, index=timeseries)
        statistics["CAGR"] = perf.create_cagr(self.equity)  # added

        return statistics

    def _calculate_sharpe(self, benchmark_return=0.00, period=252):
        """
        Calculate the sharpe ratio of our equity_returns.
        Expects benchmark_return to be, for example, 0.01 for 1%
        """
        xs_rtrns = pd.Series(self.equity_returns) - benchmark_return / 252    # pd.series to avoid type mismatch
        # noinspection PyUnresolvedReferences
        annualised_sharpe = np.sqrt(period) * xs_rtrns.mean() / xs_rtrns.std()
        return round(annualised_sharpe, 4)

    def _calculate_max_drawdown_pct(self):
        """
        Calculate the percentage drop related to the "worst"
        drawdown seen.
        """
        drawdown_series = pd.Series(self.drawdowns)
        equity_series = pd.Series(self.equity)
        bottom_index = drawdown_series.idxmax()
        try:
            top_index = equity_series[:bottom_index].idxmax()   # top preceding the worse bottom
            pct = (
                (equity_series.ix[top_index] - equity_series.ix[bottom_index]) / 
                equity_series.ix[top_index] * 100
            )
            return round(pct, 4)
        except ValueError:
            return np.nan

    def plot_results(self):
        """
        A simple script to plot the balance of the portfolio, or
        "equity curve", as a function of time.
        """
        sns.set_palette("deep", desat=.6)
        sns.set_context(rc={"figure.figsize": (8, 4)})

        # Plot 3 charts: Equity curve, period returns, drawdowns
        fig = plt.figure()
        fig.patch.set_facecolor('white')

        # get equity curve / eq rtrns / drawdowns
        df = self._get_equity_df()

        print("Plotting equity curve and drawdowns...")

        # Plot the equity curve
        ax1 = fig.add_subplot(311, ylabel='Equity Value')
        df["equity"].plot(ax=ax1, color=sns.color_palette()[0])

        # Plot the returns
        ax2 = fig.add_subplot(312, ylabel='Equity Returns')
        df['equity_returns'].plot(ax=ax2, color=sns.color_palette()[1], lw=2.)

        # drawdown, max_dd, dd_duration = self.create_drawdowns(df["Equity"])
        ax3 = fig.add_subplot(313, ylabel='Drawdowns')
        df['drawdowns'].plot(ax=ax3, color=sns.color_palette()[2], lw=2.)

        # Rotate dates
        fig.autofmt_xdate()

        # Plot the figure
        plt.show()

    # NB: there's extra-first day... that's the reason for [1:]
    # TODO: check reason for extra-day
    def _get_equity_df(self):
        df = pd.DataFrame()
        df["equity"] = pd.Series(self.equity[1:], index=self.timeseries[1:])
        df["equity_returns"] = pd.Series(self.equity_returns[1:], index=self.timeseries[1:])
        df["drawdowns"] = pd.Series(self.drawdowns[1:], index=self.timeseries[1:])
        return df

    def _get_filename(self, filename=""):
        if filename == "":
            now = datetime.datetime.utcnow()
            filename = "statistics_" + now.strftime("%Y-%m-%d_%H%M%S") + ".pkl"
            filename = os.path.expanduser(os.path.join(self.config.OUTPUT_DIR, filename))
        return filename

    def save(self, filename="", csv=True):
        # pickle the Statistics class
        filename = self._get_filename(filename)
        print("Save results to '%s'" % filename)
        with open(filename, 'wb') as fd:
            pickle.dump(self, fd)
        # save a .csv file with main series
        if csv:
            filename_csv = os.path.expanduser(os.path.join(self.config.OUTPUT_DIR, filename[:-4] + ".csv"))
            print("Save results to '%s'" % filename_csv)
            with open(filename_csv, 'wb') as fd_csv:
                self._get_equity_df().to_csv(fd_csv)

