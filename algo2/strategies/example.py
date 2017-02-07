from base_strategy import AbstractStrategy
from algo2.event import (SignalEvent, EventType)


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

        # Adds default values to the bars/invested dictionaries
        self.ticks = {ticker: 0 for ticker in self.tickers}     # was: self.ticks = 0
        self.invested = {ticker: False for ticker in self.tickers}  # was: self.invested = False

    def calculate_signals(self, event):
        if event.type == EventType.TICK:    # and event.ticker == ticker:
            tkr = event.ticker  # was: ticker = self.tickers[0]
            if self.ticks[tkr] % 5 == 0:
                if not self.invested[tkr]:
                    signal = SignalEvent(tkr, "BOT")
                    self.events_queue.put(signal)
                    self.invested[tkr] = True
                else:
                    signal = SignalEvent(tkr, "SLD")
                    self.events_queue.put(signal)
                    self.invested[tkr] = False
            self.ticks[tkr] += 1
