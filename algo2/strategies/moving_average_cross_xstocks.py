from collections import deque
import numpy as np

from base_strategy import AbstractStrategy
from algo2.event import (SignalEvent, EventType)


# TODO: remove first class (1 ticker only) once second below tested
# MA cross for STOCKS either:
#   i. long (if sma > lma) or
#   ii. flat
##########################################################
class MovingAverageCrossStrategy(AbstractStrategy):
    """
    long if sma > lma, flat otherwise

    :param tickers - The list of ticker symbols
    :param events_queue - A handle to the system events queue
    :param short_window - Lookback period for short moving average
    :param long_window - Lookback period for long moving average
    """
    def __init__(
        self, tickers, events_queue,
        short_window=100, long_window=400
    ):
        self.tickers = tickers
        self.events_queue = events_queue

        self.short_window = short_window
        self.long_window = long_window

        self.bars = 0
        self.invested = False

        self.sw_bars = deque(maxlen=self.short_window)
        self.lw_bars = deque(maxlen=self.long_window)

    def calculate_signals(self, event):
        # NB: Only applies SMA to first ticker
        ticker = self.tickers[0]
        if event.type == EventType.BAR and event.ticker == ticker:

            # Add latest adjusted closing price to short and long window bars
            self.lw_bars.append(event.adj_close_price)
            if self.bars > self.long_window - self.short_window:    # TODO: can probably eliminate the 'if'
                self.sw_bars.append(event.adj_close_price)

            # Enough bars are present for trading
            if self.bars > self.long_window:
                # Calculate the simple moving averages
                short_sma = np.mean(self.sw_bars)
                long_sma = np.mean(self.lw_bars)

                # Trading signals based on moving average cross
                if short_sma > long_sma and not self.invested:
                    print("LONG: %s" % event.time)
                    signal = SignalEvent(ticker, "BOT")
                    self.events_queue.put(signal)
                    self.invested = True
                elif short_sma < long_sma and self.invested:
                    print("SHORT: %s" % event.time)
                    signal = SignalEvent(ticker, "SLD")
                    self.events_queue.put(signal)
                    self.invested = False

            self.bars += 1


##########################################################
class NEWMovingAverageCrossStrategyNEW(AbstractStrategy):
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
        self.bars, self.invested, self.sw_bars, self.lw_bars = self._calculate_initial

    def _calculate_initial(self):
        """
        Adds default values to bars and invested and sw_bars/lw_bars
        """
        bars = {}
        invested = {}
        sw_bars = {}
        lw_bars = {}
        for tkr in self.tickers:
            bars[tkr] = 0
            invested[tkr] = False
            sw_bars[tkr] = deque(maxlen=self.short_window)
            lw_bars[tkr] = deque(maxlen=self.long_window)
        return bars, invested, sw_bars, lw_bars

    def calculate_signals(self, event):
        for tkr in self.tickers:
            if event[tkr].type == EventType.BAR and event[tkr].ticker == tkr:
                # Add latest adjusted closing price to both windows
                self.lw_bars[tkr].append(event.adj_close_price)  # earlier: getting get_bar[-window]
                if self.bars[tkr] > self.long_window - self.short_window:
                    self.sw_bars[tkr].append(event.adj_close_price)
                # Enough bars are present for trading
                if self.bars[tkr] > self.long_window:
                    # Calculate the simple moving averages
                    short_sma = np.mean(self.sw_bars[tkr])       # earlier: np.mean(bars[-self.short_window:])
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
                        self.invested[tkr] = False  # get out of the market
                self.bars += 1
