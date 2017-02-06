from Algo2.pos_sizers.base_sizer import AbstractPositionSizer


class NaiveStockPosSizer(AbstractPositionSizer):

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


class NaiveFuturesPosSizer(AbstractPositionSizer):

    def __init__(self, default_quantity=1):
        self.default_quantity = default_quantity

    def size_order(self, portfolio, initial_order):
        """
        This NaivePositionSizer object follows all
        suggestions from the initial order without
        modification.
        """
        return initial_order


#################################################
class FixedPositionSizer(AbstractPositionSizer):
    def __init__(self, default_quantity=100):
        self.default_quantity = default_quantity

    def size_order(self, portfolio, initial_order):
        """
        This FixedPositionSizer object simply modifies
        the quantity to be 100 of any share transacted.
        """
        initial_order.quantity = self.default_quantity
        return initial_order
