from algo2.strategies.base_strategy import AbstractStrategy
from algo2.event import (SignalEvent, EventType)


class BuyAndHoldStrategy(AbstractStrategy):
    """
    A testing strategy that simply purchases (a set of)
    asset(s) upon first relevant market event and
    then hold it/them until end of back-testing.
    """
    def __init__(self, tickers, events_queue):
        self.tickers = tickers
        self.events_queue = events_queue

        # Adds default values to the bars/invested dictionaries
        self.ticks = {ticker: 0 for ticker in self.tickers}
        self.invested = {ticker: False for ticker in self.tickers}

    def calculate_signals(self, event):
        tkr = event.ticker
        if event.type in [EventType.BAR, EventType.TICK]:
            if not self.invested[tkr] and self.ticks[tkr] == 0:
                signal = SignalEvent(tkr, "BOT")
                self.events_queue.put(signal)
                self.invested[tkr] = True
            self.ticks[tkr] += 1
