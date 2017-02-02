from Algo2.strategy import AbstractStrategy
from Algo2.event import (SignalEvent, EventType)


class BuyAndHoldStrategy(AbstractStrategy):
    """
    A testing strategy that simply purchases (a set of)
    asset(s) upon first relevant market event and
    then hold it/them until end of backtest.
    """
    def __init__(self, tickers, events_queue):
        self.tickers = tickers
        self.events_queue = events_queue
        self.ticks = 0
        self.invested = False

    def calculate_signals(self, event):
        ticker = self.tickers[0]
        if event.type in [EventType.BAR, EventType.TICK] and event.ticker == ticker:
            if not self.invested and self.ticks == 0:
                signal = SignalEvent(ticker, "BOT")
                self.events_queue.put(signal)
                self.invested = True
            self.ticks += 1
