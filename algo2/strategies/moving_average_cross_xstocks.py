#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import deque
import numpy as np

from algo2.strategies.base_strategy import AbstractStrategy
from algo2.event import (SignalEvent, EventType)


# MA cross for STOCKS either:
#   i. long (if sma > lma) or
#   ii. flat
# TODO: generalised for more tickers, CHECK that works
##########################################################
class MovingAverageCrossStrategy(AbstractStrategy):
    """
    Long only cross moving avg.
    :param tickers - list of ticker symbols;
    :param events_queue - A handle to the system events queue;
    :param short_window - Lookback period for short moving average;
    :param long_window - Lookback period for long moving average.
    """
    def __init__(
        self, tickers, events_queue,
        short_window=50, long_window=200
    ):
        self.tickers = tickers
        self.events_queue = events_queue

        self.short_window = short_window
        self.long_window = long_window

        # initial no. of bars (zero) and if invested in the market (False)
        self.bars = {ticker: 0 for ticker in self.tickers}  # self.bars = 0
        self.invested = {ticker: False for ticker in self.tickers}  # self.invested = False

        # initialise deque's for sma and lma
        self.sw_bars, self.lw_bars = self._calculate_initial()

    def _calculate_initial(self):
        """
        Adds default values to sw_bars/lw_bars
        """
        sw_bars = {}
        lw_bars = {}
        for tkr in self.tickers:
            sw_bars[tkr] = deque(maxlen=self.short_window)
            lw_bars[tkr] = deque(maxlen=self.long_window)
        return sw_bars, lw_bars

    def calculate_signals(self, event):
        if event.type == EventType.BAR:  # and event.ticker == tkr:
            tkr = event.ticker

            # Add latest adjust close prices
            # ted closing price to short and long window bars
            self.lw_bars[tkr].append(event.adj_close_price)
            if self.bars[tkr] > self.long_window - self.short_window:  # TODO: can probably eliminate the 'if'
                self.sw_bars[tkr].append(event.adj_close_price)

            # Enough bars are present for trading
            if self.bars[tkr] > self.long_window:
                # Calculate the simple moving averages
                short_sma = np.mean(self.sw_bars[tkr])
                long_sma = np.mean(self.lw_bars[tkr])

                # Trading signals based on moving average cross
                if short_sma > long_sma and not self.invested[tkr]:
                    print("LONG: %s" % event.time)
                    signal = SignalEvent(tkr, "BOT")
                    self.events_queue.put(signal)
                    self.invested[tkr] = True
                elif short_sma < long_sma and self.invested[tkr]:
                    print("SHORT: %s" % event.time)
                    signal = SignalEvent(tkr, "SLD")
                    self.events_queue.put(signal)
                    self.invested[tkr] = False

            self.bars[tkr] += 1
