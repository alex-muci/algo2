from Algo2.strategies.base_strategy import AbstractStrategy
from Algo2.event import (SignalEvent, EventType)


# TODO: remove first class (1 ticker only) once second below tested
#############################################
class BuyAndHoldStrategy(AbstractStrategy):
    """
    A testing strategy that simply purchases (longs) a set of
    assets upon first receipt of the relevant bar event and
    then holds until the completion of a backtest.
    """
    def __init__(self, tickers, events_queue):
        self.tickers = tickers
        self.events_queue = events_queue
        self.ticks = 0
        self.invested = False

    def calculate_signals(self, event):
        # only for 1st ticker only
        ticker = self.tickers[0]
        if event.type in [EventType.BAR, EventType.TICK] and event.ticker == ticker:
            if not self.invested and self.ticks == 0:
                signal = SignalEvent(ticker, "BOT")
                self.events_queue.put(signal)
                self.invested = True
            self.ticks += 1


#############################################
class NEWBuyAndHoldStrategyNEW(AbstractStrategy):
    """
    A testing strategy that simply purchases (a set of)
    asset(s) upon first relevant market event and
    then hold it/them until end of back-testing.
    """
    def __init__(self, tickers, events_queue):
        self.tickers = tickers
        self.events_queue = events_queue

        self.ticks, self.invested = self._calculate_initial()

    def _calculate_initial(self):
        """
        Adds default values to the bars/invested dictionaries
        """
        ticks = {ticker: 0 for ticker in self.tickers}
        invested = {ticker: False for ticker in self.tickers}
        return ticks, invested

    def calculate_signals(self, event):
        for tkr in self.tickers:
            if event[tkr].type in [EventType.BAR, EventType.TICK] and event[tkr].ticker == tkr:
                if not self.invested[tkr] and self.ticks[tkr] == 0:
                    signal = SignalEvent(tkr, "BOT")
                    self.events_queue.put(signal)
                    self.invested[tkr] = True
                self.ticks[tkr] += 1
