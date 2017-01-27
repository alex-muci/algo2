from base_sizer import AbstractPositionSizer


class Stock_NaivePositionSizer(AbstractPositionSizer):
    def __init__(self, default_quantity=100):
        self.default_quantity = default_quantity

    def size_order(self, portfolio, initial_order):
        """
        This NaivePositionSizer object follows all
        suggestions from the initial order without
        modification.
        """
        # initial_order.quantity = self.default_quantity # un-commenting this makes qnty = default one (=100)
        return initial_order

class Futures_NaivePositionSizer(AbstractPositionSizer):
    def __init__(self, default_quantity=1):
        self.default_quantity = default_quantity

    def size_order(self, portfolio, initial_order):
        """
        This NaivePositionSizer object follows all
        suggestions from the initial order without
        modification.
        """
        return initial_order
