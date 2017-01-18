#!/usr/bin/python
# -*- coding: utf-8  -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


from enum import Enum
EventType = Enum("EventType", "TICK BAR SIGNAL ORDER FILL")
##########################################
class Event(object):
    """
    Event is the base class, provinding an interface
    for all inherited that will be created/stored
    
    @property
    def typename(self):
        return self.type.name
    """
    pass

##########################################
class MarketEvent(Event):
    """
    Handles the event of receiving a new market update
    and triggers Strategy to generate signals.
    
    Datafeed ->  MarketEvent -> Strategy
    """
    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = 'MARKET'

# MarketEvent 
# can be expressed in one of the following ways:
class TickEvent(Event):
    """
    Handles the event of receiving a new market update tick,
    which is defined as a ticker symbol and associated best
    bid and ask from the top of the order book.
    """
    def __init__(self, ticker, time, bid, ask):
        """
        Initialises the TickEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'GOOG'.
        time - The timestamp of the tick
        bid - The best bid price at the time of the tick.
        ask - The best ask price at the time of the tick.
        """
        self.type = EventType.TICK # i.e. = "TICK" 
        self.ticker = ticker
        self.time = time
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return "Type: %s, Ticker: %s, Time: %s, Bid: %s, Ask: %s" % (
            str(self.type), str(self.ticker),
            str(self.time), str(self.bid), str(self.ask)
        )

    def __repr__(self):
        return str(self)


class BarEvent(Event):
    """
    Handles the event of receiving a new market
    open-high-low-close-volume bar, as would be generated
    via common data providers such as Yahoo Finance.
    """
    def __init__(
        self, ticker, time, period,
        open_price, high_price, low_price,
        close_price, volume, adj_close_price=None
    ):
        """
        Initialises the BarEvent.

        Parameters:
        ticker - The ticker symbol, e.g. 'GOOG'.
        time - The timestamp of the bar
        period - The time period covered by the bar in seconds
        open_price - The unadjusted opening price of the bar
        high_price - The unadjusted high price of the bar
        low_price - The unadjusted low price of the bar
        close_price - The unadjusted close price of the bar
        volume - The volume of trading within the bar
        adj_close_price - The vendor adjusted closing price
            (e.g. back-adjustment) of the bar

        Note: It is not advised to use 'open', 'close' instead
        of 'open_price', 'close_price' as 'open' is a reserved
        word in Python.
        """
        self.type = EventType.BAR   # i.e. = "BAR" 
        self.ticker = ticker
        self.time = time
        self.period = period
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume
        self.adj_close_price = adj_close_price
        self.period_readable = self._readable_period()

    def _readable_period(self):
        """
        Creates a human-readable period from the number
        of seconds specified for 'period'.

        For instance, converts:
        * 1 -> '1sec'
        * 5 -> '5secs'
        * 60 -> '1min'
        * 300 -> '5min'

        If no period is found in the lookup table, the human
        readable period is simply passed through from period,
        in seconds.
        """
        lut = {
            1: "1sec",
            5: "5sec",
            10: "10sec",
            15: "15sec",
            30: "30sec",
            60: "1min",
            300: "5min",
            600: "10min",
            900: "15min",
            1800: "30min",
            3600: "1hr",
            86400: "1day",
            604800: "1wk"
        }
        if self.period in lut:
            return lut[self.period]
        else:
            return "%ssec" % str(self.period)

    def __str__(self):
        format_str = "Type: %s, Ticker: %s, Time: %s, Period: %s, " \
            "Open: %s, High: %s, Low: %s, Close: %s, " \
            "Adj Close: %s, Volume: %s" % (
                str(self.type), str(self.ticker), str(self.time),
                str(self.period_readable), str(self.open_price),
                str(self.high_price), str(self.low_price),
                str(self.close_price), str(self.adj_close_price),
                str(self.volume)
            )
        return format_str

    def __repr__(self):
        return str(self)

##########################################
class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    Strategy -> SignalEvent -> Portfolio (splittable in sizer and risk mgt)
    """
    def __init__(self, strategy_id, symbol, datetime, signal_type, strength):
        """
        Initialises the SignalEvent.

        Parameters:
        strategy_id - unique ID of the strategy generating the signal.
        symbol - ticker symbol
        datetime - timestamp at which the signal was generated.
        signal_type - either 'LONG' or 'SHORT'.
        strength - adjustment factor "suggestion" used to scale 
            quantity at the portfolio level. Useful for pairs strategies.
        """
        self.strategy_id = strategy_id
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength
##########################################
class SuggestedOrderEvent(Event):
    """
    A SuggestedOrder object is generated by the PortfolioHandler
    to be sent to the PositionSizer object and subsequently the
    RiskManager object. Creating a separate object type for
    suggested orders and final orders (OrderEvent objects) ensures
    that a suggested order is never transacted unless it has been
    scrutinised by the position sizing and risk management layers.
    """
    def __init__(self, symbol, order_type, quantity=0):
        """
        Initialises the SuggestedOrder. The quantity defaults
        to zero as the PortfolioHandler creates these objects
        prior to any position sizing.

        The PositionSizer object will "fill in" the correct
        value prior to sending the SuggestedOrder to the
        RiskManager.

        Parameters:
        symbol - The ticker symbol, e.g. 'GOOG'.
        order_type - 'BOT' (for long) or 'SLD' (for short)
            or 'EXIT' (for liquidation).
        quantity - The quantity of shares to transact.
        """
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity

##########################################
class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    Portfolio -> OrderEvent -> Execution
    """

    def __init__(self, symbol, order_type, quantity, direction):
        """
        Initialises 
        1. order type, either Market order ('MKT') or Limit order ('LMT'), 
        2. quantity (integral) and 
        3. its direction ('BUY' or 'SELL').

        TODO: Must handle error checking here to obtain 
        rational orders (i.e. no negative quantities etc).

        Parameters:
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        """
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print(
            "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % 
            (self.symbol, self.order_type, self.quantity, self.direction)
        )

##########################################
class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    
    TODO: Currently does not support filling positions at
    different prices. This will be simulated by averaging
    the cost.
    """

    def __init__(self, timeindex, symbol, exchange, quantity, 
                 direction, fill_cost, commission=None):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional 
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        timeindex - The bar-resolution when the order was filled (i.e. datetime).
        symbol - The instrument which was filled.
        exchange - The exchange where the order was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        fill_cost - The holdings value in dollars.
        commission - An optional commission sent from IB.
        """
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        # Calculate commission
        if commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission

    def calculate_ib_commission(self):
        """
        Calculates the fees of trading based on an Interactive
        Brokers fee structure for API, in USD.

        This does not include exchange or ECN fees.

        Based on "US API Directed Orders":
        https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
        """
        full_cost = 1.3
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else: # Greater than 500
            full_cost = max(1.3, 0.008 * self.quantity)
        return full_cost