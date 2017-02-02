#from __future__ import print_function

from .utilities import queue
from .event import EventType


class Backtest(object):
    """
    Encapsulates the settings and components for
    carrying out an event-driven backtesting.
    """
    def __init__(
        self, data_handler,
        strategy, portfolio_handler, broker,
        position_sizer, risk_manager,
        statistics, equity
    ):
        """
        Set up backtesting variables according to
        what has been passed in.
        """
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio_handler = portfolio_handler
        self.broker = broker
        self.position_sizer = position_sizer
        self.risk_manager = risk_manager
        self.statistics = statistics
        self.equity = equity

        self.events_queue = data_handler.events_queue   # = queue.Queue()
        self.cur_time = None

    def _run_backtest(self):
        """
        Carries out an infinite while loop that polls the
        events queue and directs each event to either the
        strategy component of the execution handler. The
        loop continue until the event queue has been
        emptied.
        """
        print("Running Backtest...")
        while self.data_handler.continue_backtest:
            try:
                event = self.events_queue.get(False)
            except queue.Empty:
                self.data_handler.stream_next()  # get next bar
            else:
                if event is not None:
                    if event.type == EventType.TICK or event.type == EventType.BAR:
                        self.cur_time = event.time
                        self.strategy.calculate_signals(event)
                        self.portfolio_handler.update_portfolio_value()
                        self.statistics.update(event.time, self.portfolio_handler)
                    elif event.type == EventType.SIGNAL:
                        self.portfolio_handler.on_signal(event)
                    elif event.type == EventType.ORDER:
                        self.broker.execute_order(event)
                    elif event.type == EventType.FILL:
                        self.portfolio_handler.on_fill(event)
                    else:
                        raise NotImplemented("Unsupported event.type '%s'" % event.type)

    def simulate_trading(self, testing=False):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        results = self.statistics.get_results()
        print("---------------------------------")
        print("Backtest complete.")
        print("Sharpe Ratio: %s" % results["sharpe"])
        print("Max Drawdown: %s" % results["max_drawdown"])
        print("Max Drawdown Pct: %s" % results["max_drawdown_pct"])
        if not testing:
            self.statistics.plot_results()
        return results
