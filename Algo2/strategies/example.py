from base_strategy import AbstractStrategy
from Algo2.event import (SignalEvent, EventType)


# TODO: works for one ticker only
class ExampleStrategy(AbstractStrategy):
    """
    Testing strategy that alternates buying and selling
    a ticker on every 5th tick. This has the effect of continuously
    "crossing the spread" and so will be loss-making strategy.

    It is used to test that the backtester/live trading system is
    behaving as expected.
    """
    def __init__(self, tickers, events_queue):
        self.tickers = tickers
        self.events_queue = events_queue
        self.ticks = 0
        self.invested = False

    def calculate_signals(self, event):
        ticker = self.tickers[0]    # just for the 1st ticker only
        if event.type == EventType.TICK and event.ticker == ticker:
            if self.ticks % 5 == 0:
                if not self.invested:
                    signal = SignalEvent(ticker, "BOT")
                    self.events_queue.put(signal)
                    self.invested = True
                else:
                    signal = SignalEvent(ticker, "SLD")
                    self.events_queue.put(signal)
                    self.invested = False
            self.ticks += 1
