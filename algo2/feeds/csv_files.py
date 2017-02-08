#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import pandas as pd

from algo2.event import BarEvent, TickEvent
from algo2.feeds.base_feed import AbstractBarDataHandler, AbstractTickDataHandler


# TODO: add open/high/low in 'subscribe'
class HistoricCSVBarDataHandler(AbstractBarDataHandler):
    """
    HistoricCSVBarDataHandler is designed to read CSV files of
    Yahoo Finance daily Open-High-Low-Close-Volume (OHLCV) data
    for each requested financial instrument and stream those to
    the provided events queue as BarEvents.
    """
    def __init__(
        self, csv_dir, events_queue,
        init_tickers=None,
        start_date=None, end_date=None
    ):
        """
        Takes the CSV directory, the events queue and a possible
        list of initial ticker symbols then creates an (optional)
        list of ticker subscriptions and associated prices.
        """
        self.csv_dir = csv_dir
        self.events_queue = events_queue
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker)
        self.start_date = start_date
        self.end_date = end_date
        self.bar_stream = self._merge_sort_ticker_data()

    def _open_ticker_price_csv(self, ticker):
        """
        Opens the CSV files containing the equities ticks from
        the specified CSV data directory, converting them into
        them into a pandas DataFrame, stored in a dictionary.
        """
        ticker_path = os.path.join(self.csv_dir, "%s.csv" % ticker)
        self.tickers_data[ticker] = pd.read_csv(
            ticker_path, header=0, parse_dates=True,
            index_col=0, names=(
                "Date", "Open", "High", "Low",
                "Close", "Volume", "Adj Close"
            )
        )
        self.tickers_data[ticker]["Ticker"] = ticker

    def _merge_sort_ticker_data(self):
        """
        Concatenates all of the separate equities DataFrames
        into a single DataFrame that is time ordered, allowing tick
        data events to be added to the queue in a chronological fashion.

        Note that this is an idealised situation, utilised solely for
        backtesting. In live trading ticks may arrive "out of order".
        """
        # .sort_index(inplace=True) if not copy
        df = pd.concat(self.tickers_data.values()).sort_index()

        start = None
        end = None
        # get the indices if 'start_date' or 'end_end' in __init__
        if self.start_date is not None:
            start = df.index.searchsorted(self.start_date)
        if self.end_date is not None:
            end = df.index.searchsorted(self.end_date)

        # Determine how to slice data
        if start is None and end is None:
            return df.iterrows()    # default, as per the Tick version below
        elif start is not None and end is None:
            return df.ix[start:].iterrows()
        elif start is None and end is not None:
            return df.ix[:end].iterrows()
        else:
            return df.ix[start:end].iterrows()

    def subscribe_ticker(self, ticker):
        """
        Subscribes the data handler to a new ticker symbol.
        """
        if ticker not in self.tickers:
            try:
                self._open_ticker_price_csv(ticker)
                dft = self.tickers_data[ticker]
                row0 = dft.iloc[0]

                # open = float(row0["Open"])
                # etc..

                ticker_prices = {
                    "close": float(row0["Close"]),
                    "adj_close": float(row0["Adj Close"]),
                    "timestamp": dft.index[0]
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                print(
                    "Could not subscribe ticker %s "
                    "as no data CSV found for pricing." % ticker
                )
        else:
            print(
                "Could not subscribe ticker %s "
                "as is already subscribed." % ticker
            )

    def _create_event(self, index, period, ticker, row):
        """
        Obtain all elements of the bar from a row of dataframe
        and return a BarEvent
        """
        open_price = float(row["Open"])
        high_price = float(row["High"])
        low_price = float(row["Low"])
        close_price = float(row["Close"])
        adj_close_price = float(row["Adj Close"])
        volume = int(row["Volume"])
        bev = BarEvent(
            ticker, index, period, open_price,
            high_price, low_price, close_price,
            volume, adj_close_price
        )
        return bev

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """
        try:
            index, row = next(self.bar_stream)
        except StopIteration:
            self.continue_backtest = False
            return
        # Obtain all elements of the bar from the dataframe
        ticker = row["Ticker"]
        period = 86400  # Seconds in a day
        # Create the tick event for the queue
        bev = self._create_event(index, period, ticker, row)
        # Store event
        self._store_event(bev)  # method of the underlying class
        # Send event to queue
        self.events_queue.put(bev)

#############################################################
#############################################################


class HistoricCSVTickDataHandler(AbstractTickDataHandler):
    """
    HistoricCSVPrDataHandler is designed to read CSV files of
    tick data for each requested financial instrument and
    stream those to the provided events queue as TickEvents.
    """
    def __init__(self, csv_dir, events_queue, init_tickers=None):
        """
        Takes the CSV directory, the events queue and a possible
        list of initial ticker symbols, then creates an (optional)
        list of ticker subscriptions and associated prices.
        """
        self.csv_dir = csv_dir
        self.events_queue = events_queue
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker)
        self.tick_stream = self._merge_sort_ticker_data()

    def _open_ticker_price_csv(self, ticker):
        """
        Opens the CSV files containing the equities ticks from
        the specified CSV data directory, converting them into
        them into a pandas DataFrame, stored in a dictionary.
        """
        ticker_path = os.path.join(self.csv_dir, "%s.csv" % ticker)
        self.tickers_data[ticker] = pd.read_csv(
            ticker_path, header=0, parse_dates=True,
            dayfirst=True, index_col=1,
            names=("Ticker", "Time", "Bid", "Ask")
        )

    def _merge_sort_ticker_data(self):
        """
        Concatenates all of the separate equities DataFrames
        into a single DataFrame that is time ordered, allowing tick
        data events to be added to the queue in a chronological fashion.
        Note that this is an idealised situation, utilised solely for
        backtesting. In live trading ticks may arrive "out of order".
        """
        return pd.concat(
            self.tickers_data.values()
        ).sort_index().iterrows()

    def subscribe_ticker(self, ticker):
        """
        Subscribes the price handler to a new ticker symbol.
        """
        if ticker not in self.tickers:
            try:
                self._open_ticker_price_csv(ticker)
                dft = self.tickers_data[ticker]
                row0 = dft.iloc[0]
                ticker_prices = {
                    "bid": float(row0["Bid"]),
                    "ask": float(row0["Ask"]),
                    "timestamp": dft.index[0]
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                print(
                    "Could not subscribe ticker %s "
                    "as no data CSV found for pricing." % ticker
                )
        else:
            print(
                "Could not subscribe ticker %s "
                "as is already subscribed." % ticker
            )

    def _create_event(self, index, ticker, row):
        """
        Obtain all elements of the bar a row of dataframe
        and return a TickEvent
        """
        bid = float(row["Bid"])
        ask = float(row["Ask"])
        tev = TickEvent(ticker, index, bid, ask)
        return tev

    def stream_next(self):
        """
        Place the next TickEvent onto the event queue.
        """
        try:
            index, row = next(self.tick_stream)
        except StopIteration:
            self.continue_backtest = False
            return
        ticker = row["Ticker"]
        tev = self._create_event(index, ticker, row)
        self._store_event(tev)
        self.events_queue.put(tev)
