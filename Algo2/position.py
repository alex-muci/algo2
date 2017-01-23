from __future__ import division
from numpy import sign
# from abc import ABCMeta, abstractmethod

#########################################################
# TO DO:
#    - DOMESTIC CURRENCY conversion
#    - create ABC Position: 2 methods (update_value, trade)
#    - rename class Position below into SharesPosition
#    - create FuturesPosition
#
#    - CHECK definition in Interactive Brokers TWS, 
#      e.g. https://www.interactivebrokers.com/en/software/tws/usersguidebook/thetradingwindow/position_and_p___l.htm
#########################################################


class Position(object):
    """
    Book-keeping for initial shares qnty/value and 
    following trades in same shares.
    """
    def __init__(
        self, order_type, symbol, 
        init_quantity, init_price, init_commission,
        bid, ask   # for future ticks implementation (rather than just daily close)
    ):
        """
        Initial booking-keeping is set for zero expect for initial sales/buys,
        then calculates initial values and market/pnl values.
        """
        self.order_type = order_type
        self.symbol = symbol
        self.quantity = init_quantity
        self.price = init_price
        self.commission = init_commission

        self.total_commission = init_commission # in 'trade'
        
        self.buys, self.sells = 0, 0           # = qnty (for bot or sld)
        self.avg_bot, self.avg_sld = 0, 0      # = prices (for bot or sld)
        self.total_bot, self.total_sld = 0, 0  # = price * qnty
        
        self._calculate_initial_value() # avgs and totals above, avg price (incl. comm) and full cost 
        
        self.update_value(bid, ask) # market_value and pnl (un-/realised) 

    def _calculate_initial_value(self):
        """
        Depending upon whether the order_type was a buy or sell ("BOT"
        or "SLD") calculate average and total cost, average price and the (full) cost.
        Finally, calculate the net total with and without commission.
        """
        if self.order_type == "BOT":
            self.buys = self.quantity  # initial quantity
            self.avg_bot = self.price # initial price
            self.total_bot = self.buys * self.avg_bot
            self.avg_price = (self.price * self.quantity + self.commission) / self.quantity
            self.cost = self.quantity * self.avg_price
        else:  # order_type == "SLD"
            self.sells = self.quantity  # initial quantity
            self.avg_sld = self.price # initial price
            self.total_sld = self.sells * self.avg_sld
            self.avg_price = (self.price * self.quantity - self.commission) / self.quantity
            self.cost = -self.quantity * self.avg_price
            
        self.net = self.buys - self.sells                   # net quantity 
        self.net_total = self.total_sld - self.total_bot    # net dollar amount, without commission
        self.net_incl_comm = self.net_total - self.commission # net dollar amount, WITH commission

    def update_value(self, bid, ask):
        """
        Market value estimated via the mid-price of the
        bid-ask spread, incl calculation of the unrealised 
        and realised profit & loss.
        """
        midpoint = (bid + ask) / 2  
        self.market_value = self.quantity * midpoint * sign(self.net)
        self.unrealised_pnl = self.market_value - self.cost # (current_price - avg price) * current_qnty
        self.realised_pnl = self.market_value + self.net_incl_comm   

    def trade(self, order_type, quantity, price, commission):
        """
        Calculates the adjustments to Position 
        once new shares are bought and sold.

        Updates the average bought/sold, total
        bought/sold, the cost and PnL calculations.
        """
        self.total_commission += commission

        # Upadate total bought and sold
        if order_type == "BOT":
            self.avg_bot = (self.avg_bot * self.buys + price * quantity) / (self.buys + quantity)
            if self.order_type != "SLD":
                self.avg_price = (self.avg_price * self.buys + price * quantity + commission) / (self.buys + quantity)
            self.buys += quantity
            self.total_bot = self.buys * self.avg_bot     
        elif order_type == "SLD":  
            self.avg_sld = (self.avg_sld * self.sells + price * quantity) / (self.sells + quantity)
            if self.order_type != "BOT":
                self.avg_price = (self.avg_price * self.sells + price * quantity - commission) / (self.sells + quantity)
            self.sells += quantity
            self.total_sld = self.sells * self.avg_sld
        else:
            raise NotImplemented("Unsupported order_type '%s'" % order_type)
        
        # Upadate net values
        self.net = self.buys - self.sells
        self.net_total = self.total_sld - self.total_bot
        self.net_incl_comm = self.net_total - self.total_commission

        # Upadate qnty and full cost basis
        self.quantity = self.net 
        self.cost = self.quantity * self.avg_price # TWS: Cost Basis = the current position x average price
