from Algo2.positions.stock import Stock



class Portfolio(object):
    def __init__(self, price_handler, cash):
        """
        On creation, the Portfolio object contains no
        positions and all values are "reset" to the initial
        cash, with no PnL - realised or unrealised.
        
        :method: trade_position, 
                 i.e. add new or modify existing one (+ update value)

        NB: realised_pnl is:
            - pnl from actual closed positions, plus 
            - (un) realised_pnl from still open positions.
        """
        self.price_handler = price_handler
        
        self.init_cash = cash
        self.equity = cash
        self.cur_cash = cash
        
        self.positions = {}
        self.closed_positions = []
        self.realised_pnl = 0

    def _update_portfolio(self):
        """
        Updates value of all positions that are currently open.
        Value of closed positions is booked into (self.)realised_pnl.
        """
        self.unrealised_pnl = 0
        self.equity = self.realised_pnl
        self.equity += self.init_cash

        for symbol in self.positions:
            pt = self.positions[symbol]
#           if self.price_handler.istick():
#               bid, ask = self.price_handler.get_best_bid_ask(symbol)
#           else:
            close_price = self.price_handler.get_latest_bar_value(symbol)
            bid, ask = close_price
            
            pt.update_value(bid, ask)
            self.unrealised_pnl += pt.unrealised_pnl
            pnl_diff = pt.realised_pnl - pt.unrealised_pnl
            self.equity += (
                pt.market_value - pt.cost + pnl_diff
            )

    def _add_position(
        self, order_type, symbol,
        quantity, price, commission
    ):
        """
        Adds a new Position object to the Portfolio. This
        requires getting the best bid/ask price from the
        price handler in order to calculate a reasonable
        "market value".

        Once the Position is added, the Portfolio values
        are updated.
        """
        if symbol not in self.positions:
#            if self.price_handler.istick():
#                bid, ask = self.price_handler.get_best_bid_ask(symbol)
#            else:
            close_price = self.price_handler.get_latest_bar_value(symbol)
            bid, ask = close_price

            position = Stock(
                order_type, symbol, quantity,
                price, commission, bid, ask
            )
            self.positions[symbol] = position
            self._update_portfolio()
        else:
            print(
                "Symbol %s is already in the positions list. "
                "Could not add a new position." % symbol
            )

    def _modify_position(
        self, order_type, symbol,
        quantity, price, commission
    ):
        """
        Modifies a current Position object to the Portfolio.
        This requires getting the best bid/ask price from the
        price handler in order to calculate a reasonable
        "market value".

        Once the Position is modified, the Portfolio values
        are updated.
        """
        if symbol in self.positions:
            self.positions[symbol].trade(
                order_type, quantity, price, commission
            )
#            if self.price_handler.istick():
#                bid, ask = self.price_handler.get_best_bid_ask(symbol)
#            else:
            close_price = self.price_handler.get_latest_bar_value(symbol) # get last adj close
            bid, ask = close_price

            self.positions[symbol].update_value(bid, ask)

            if self.positions[symbol].quantity == 0:
                closed = self.positions.pop(symbol)
                self.realised_pnl += closed.realised_pnl
                self.closed_positions.append(closed)

            self._update_portfolio()
        else:
            print(
                "Ticker %s not in the current position list. "
                "Could not modify a current position." % symbol
            )

    def trade_position(
        self, order_type, symbol,
        quantity, price, commission
    ):
        """
        Handles any new position or modification to
        a current position, by calling the respective
        _add_position and _modify_position methods.

        Hence, this single method will be called by the
        PortfolioHandler to update the Portfolio itself.
        """

        if order_type == "BOT":
            self.cur_cash -= ((quantity * price) + commission)
        elif order_type == "SLD":
            self.cur_cash += ((quantity * price) - commission)

        if symbol not in self.positions:
            self._add_position(
                order_type, symbol, quantity,
                price, commission
            )
        else:
            self._modify_position(
                order_type, symbol, quantity,
                price, commission
            )
