from math import floor
from base_sizer import AbstractPositionSizer


class VolTargetStockPositionSizer(AbstractPositionSizer):
    """
    Carries out a volatility target sizing
    for a Stock the order.
    """
    def __init__(self, vol_targ):

        # self.ticker_weights = ticker_weights # this is a dict

    def size_order(self, portfolio, initial_order):
        """
        Size the order to reflect the dollar-weighting of the
        current equity account size based on pre-specified
        ticker weights.
        """
        ticker = initial_order.ticker
        if initial_order.action == "EXIT":
            # Obtain current quantity and liquidate
            cur_quantity = portfolio.positions[ticker].quantity
            if cur_quantity > 0:
                initial_order.action = "SLD"
                initial_order.quantity = cur_quantity
            elif cur_quantity < 0:
                initial_order.action = "BOT"
                initial_order.quantity = cur_quantity
            else:
                initial_order.quantity = 0
        else:
            weight = self.ticker_weights[ticker]
            # Determine total portfolio value, work out dollar weight
            # and finally determine integer quantity of shares to purchase
            price = portfolio.price_handler.tickers[ticker]["adj_close"]
            dollar_weight = weight * portfolio.equity
            weighted_quantity = int(floor(dollar_weight / price))
            # Update quantity
            initial_order.quantity = weighted_quantity
        return initial_order
