#!/usr/bin/python
# -*- coding: utf-8  -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime, time
import pprint
import matplotlib.pyplot as plt
# from inspect import isclass # rather than use isistance(x, type) for new-class, which doesn't work for old-style one 

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
     
        self.events = queue.Queue() ###### <<<<  ########
     
        # you can input 1. class instances or 2. just their names (with backtesting generating the instances)
        self.data_handler = data_handler(self.events, self.csv_dir, self.symbol_list) # data_handler if isclass(data_handler) else     
        self.broker =    broker(self.events)
        self.portfolio = portfolio(self.data_handler, self.events, self.start_date, self.initial_capital) 
        self.strategy =  strategy(self.data_handler, self.events)
        
        # self.portfolio_handler = portfolio_handler
        # self.risk_manager = risk_manager
        # self.statistics = statistics
        # self.equity = equity
        # self.cur_time = None
        
        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

    
    def _run_backtest(self):
        """
        Executes the backtest.
        """        
        print("Running backtesting...")
        i = 0
        
        
        while True:
            i += 1
            print(i)
            # Update the market bars
            if self.data_handler.continue_backtest == True:
                self.data_handler.update_bars()  # MarketEvent here, see implementation of data_handler
            else:
                break
            # Handle the events
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)

                        elif event.type == 'SIGNAL':
                            self.signals += 1                            
                            self.portfolio.update_signal(event)

                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.broker.execute_order(event)

                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)
                            
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
