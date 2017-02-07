from abc import ABCMeta, abstractmethod


class AbstractPositionSizer(object):
    """
    The AbstractPositionSizer abstract class modifies
    the quantity of any instrument to be traded.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def size_order(self, portfolio, suggested_order):
        """
        This PositionSizer modifies the quantity
        of the suggested_order from Signal
        """
        raise NotImplementedError("Should implement size_order()")
