#!/usr/bin/python
# -*- coding: utf-8  -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime, time
import pprint
import matplotlib.pyplot as plt

try:
    import Queue as queue
except ImportError:
    import queue


class Backtest(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(
        self, csv_dir, symbol_list, initial_capital,
        heartbeat, start_date, data_handler, 
        broker, portfolio, strategy
    ):
        """
        Initialises the backtest.

        Parameters:
        csv_dir - The hard root to the CSV data directory.
        symbol_list - The list of symbol strings.
        intial_capital - The starting capital for the portfolio.
        heartbeat - Backtest "heartbeat" in seconds
        start_date - The start datetime of the strategy.
        data_handler - (Class) Handles the market data feed.
        broker - (Class) Handles the orders/fills for trades.
        portfolio - (Class) Keeps track of portfolio current and prior positions.
        strategy - (Class) Generates signals based on market data.
        """
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date

        self.data_handler_cls = data_handler
        self.broker_cls = broker
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy

        self.events = queue.Queue() ######
        
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1
       
        self._generate_trading_instances()

    def _generate_trading_instances(self):
        """
        Generates the trading instance objects from 
        their class types.
        """
        print(
            "Creating DataFeed, Strategy, Portfolio and Broker"
        )
        self.data_handler = self.data_handler_cls(self.events, self.csv_dir, self.symbol_list)
        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events, self.start_date, 
                                            self.initial_capital)
        self.broker = self.broker_cls(self.events)

    def _run_backtest(self):
        """
        Executes the backtest.
        """        
        print("Running backtesting...")
        i = 0
        while self.data_handler.continue_backtest:
            i += 1
            print(i)
            self.data_handler.update_bars() # MarketEvent here, see implementation of data_handler
            # Handle the events
            try:
                event = self.events.get(False)
            except queue.Empty:
                break
            else:
                if event is not None:
                    if event.type == 'MARKET':
                        self.strategy.calculate_signals(event)
                        self.portfolio.update_timeindex(event)
                    elif event.type == 'SIGNAL': # or == EventType.SIGNAL
                        self.signals += 1                            
                        self.portfolio.update_signal(event)
                    elif event.type == 'ORDER':
                        self.orders += 1
                        self.broker.execute_order(event)                        
                    elif event.type == 'FILL':
                        self.fills += 1
                        self.portfolio.update_fill(event)#
                    else:
                        raise NotImplemented("Unsupported event.type '%s'" % event.type)

        time.sleep(self.heartbeat)

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """
        self.portfolio.create_equity_curve_dataframe()
        
        print("Creating summary stats...")
        stats = self.portfolio.output_summary_stats()
        
        print("Creating equity curve...")
        print(self.portfolio.equity_curve.tail(5))
        pprint.pprint(stats)

        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)

        print("Plotting equity curve and drawdowns...") 
        fig = plt.figure();  fig.patch.set_facecolor('white') # to set the outer colour to white
        ax1 = fig.add_subplot(311, ylabel='Portfolio value, %')  
        self.portfolio.equity_curve['equity_curve'].plot(ax=ax1, color="blue", lw=2.); plt.grid(True)
        ax2 = fig.add_subplot(312, ylabel='Drawdowns, %')  
        self.portfolio.equity_curve['drawdown'].plot(ax=ax2, color="red", lw=2.); plt.grid(True)
        plt.show()
    
    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        self._output_performance()
