from numpy import sign
from __future__ import division
# from abc import ABCMeta, abstractmethod

class Position(object):
    """
    Position: book-keeping for initial shares qnty/value and 
    following trades in same shares
    """
    def __init__(
        self, order_type, symbol, init_quantity,
        init_price, init_commission,
        bid, ask   #  
    ):
        """
        Initial booking-keeping is set for zero expect for initial sales/buys,
        then get initial values and market value.
        """
        self.order_type = order_type
        self.symbol = symbol
        self.quantity = init_quantity
        self.init_price = init_price
        self.init_commission = init_commission

        self.realised_pnl, self.unrealised_pnl = 0, 0

        self.buys, self.sells = 0, 0
        self.avg_bot, self.avg_sld = 0, 0
        self.total_bot, self.total_sld = 0, 0
        self.total_commission = init_commission  # for new transactions

        self._calculate_initial_value()
        self.update_market_value(bid, ask)

    def _calculate_initial_value(self):
        """
        Depending upon whether the order_type was a buy or sell ("BOT"
        or "SLD") calculate average and total cost, average price and the full cost basis.
        Finally, calculate the net total with and without commission.
        """
        if self.order_type == "BOT":
            self.buys = self.quantity
            self.avg_bot = self.init_price
            self.total_bot = self.buys * self.avg_bot
            self.avg_price = (self.init_price * self.quantity + self.init_commission) // self.quantity
            self.cost_basis = self.quantity * self.avg_price
        else:  # order_type == "SLD"
            self.sells = self.quantity
            self.avg_sld = self.init_price
            self.total_sld = self.sells * self.avg_sld
            self.avg_price = (self.init_price * self.quantity - self.init_commission) // self.quantity
            self.cost_basis = -self.quantity * self.avg_price
            
        self.net = self.buys - self.sells                   # net quantity 
        self.net_total = self.total_sld - self.total_bot    # net dollar amount, without commission
        self.net_incl_comm = self.net_total - self.init_commission # net dollar amount, WITH commission

    def update_market_value(self, bid, ask):
        """
        Market value estimated via the mid-price of the
        bid-ask spread, incl calculation of the unrealised 
        and realised profit & loss.
        """
        midpoint = (bid + ask) // 2
        self.market_value = self.quantity * midpoint * sign(self.net)
        self.unrealised_pnl = self.market_value - self.cost_basis
        self.realised_pnl = self.market_value + self.net_incl_comm   

    def transact_shares(self, order_type, quantity, price, commission):
        """
        Calculates the adjustments to the Position that occur
        once new shares are bought and sold.

        Takes care to update the average bought/sold, total
        bought/sold, the cost basis and PnL calculations,
        as carried out through Interactive Brokers TWS.
        """
        self.total_commission += commission

        # Adjust total bought and sold
        if order_type == "BOT":
            self.avg_bot = (self.avg_bot * self.buys + price * quantity) // (self.buys + quantity)
            if self.order_type != "SLD":
                self.avg_price = (self.avg_price * self.buys + price * quantity + commission) // (self.buys + quantity)
            self.buys += quantity
            self.total_bot = self.buys * self.avg_bot     
        else: # order_type == "SLD"
            self.avg_sld = (self.avg_sld * self.sells + price * quantity) // (self.sells + quantity)
            if self.order_type != "BOT":
                self.avg_price = (self.avg_price * self.sells + price * quantity - commission) // (self.sells + quantity)
            self.sells += quantity
            self.total_sld = self.sells * self.avg_sld

        # Adjust net values
        self.net = self.buys - self.sells
        self.net_total = self.total_sld - self.total_bot
        self.net_incl_comm = self.net_total - self.total_commission

        # Update qnty and cost basis
        self.quantity = self.net 
        self.cost_basis = self.quantity * self.avg_price
