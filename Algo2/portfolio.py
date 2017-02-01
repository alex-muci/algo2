from Algo2.positions.stock import Stock


# from Algo2.positions.futures import Futures

# TODO: add futures contract


class Portfolio(object):
    def __init__(self, data_handler, cash):
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
        self.data_handler = data_handler

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

        # for each ticker gets price, update value and then sum to get port values
        for ticker in self.positions:
            pt = self.positions[ticker]
            if self.data_handler.istick():  # Tick
                bid, ask = self.data_handler.get_best_bid_ask(ticker)
            else:  # (daily) Bar
                close_price = self.data_handler.get_last_close(ticker)  # .get_latest_bar_value(ticker)
                bid, ask = close_price

            pt.update_value(bid, ask)
            self.unrealised_pnl += pt.unrealised_pnl  # += pt.market_value - pt.cost

            pnl_diff = pt.realised_pnl - pt.unrealised_pnl
            self.equity += (pt.market_value - pt.cost + pnl_diff)  # += pt.market_value + pt.net_incl_comm

    def _add_position(
            self, order_type, ticker,
            quantity, price, commission
    ):
        """
        Adds a new Stock position to the Portfolio.

        This requires:
         - getting bid/ask prices
         - create the Stock object
         - update portfolio values.
        """
        if ticker not in self.positions:  # redundant, since checked in .trade_position
            if self.data_handler.istick():
                bid, ask = self.data_handler.get_best_bid_ask(ticker)
            else:
                close_price = self.data_handler.get_latest_bar_value(ticker)
                bid, ask = close_price

            self.positions[ticker] = Stock(
                order_type, ticker, quantity,
                price, commission, bid, ask
            )
            self._update_portfolio()
        else:
            print(
                "Ticker %s is already in the positions list. "
                "Could not add a new position." % ticker
            )

    def _modify_position(
            self, order_type, ticker,
            quantity, price, commission
    ):
        """
        Modifies a current Position object to the Portfolio.
        This requires getting bid/ask prices from the
        price handler in order to calculate a reasonable
        "market value".

        Once the Position is modified, the Portfolio values
        are updated.
        """
        if ticker in self.positions:  # redundant, since checked in .trade_position
            self.positions[ticker].trade(
                order_type, quantity, price, commission
            )
            if self.data_handler.istick():
                bid, ask = self.data_handler.get_best_bid_ask(ticker)
            else:
                close_price = self.data_handler.get_latest_bar_value(ticker)  # get last adj close
                bid, ask = close_price

            self.positions[ticker].update_value(bid, ask)  # TODO: move in the 'if' below?

            # position closed
            if self.positions[ticker].quantity == 0:
                closed = self.positions.pop(ticker)
                self.realised_pnl += closed.realised_pnl
                self.closed_positions.append(closed)

            self._update_portfolio()
        else:
            print(
                "Ticker %s not in the current position list. "
                "Could not modify a current position." % ticker
            )

    def trade_position(
            self, order_type, ticker,
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

        if ticker not in self.positions:
            self._add_position(
                order_type, ticker, quantity,
                price, commission
            )
        else:
            self._modify_position(
                order_type, ticker, quantity,
                price, commission
            )
