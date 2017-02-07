from __future__ import division

from abc import ABCMeta, abstractmethod


#########################################################
# TODO:
#    - DOMESTIC CURRENCY conversion: GBPxxx = 1
#    - create ABC Position: 2 methods (update_value, trade)
#    - create FuturesPosition
#
#    - CHECK definition in Interactive Brokers TWS,
#      e.g. https://www.interactivebrokers.com/en/software/tws/usersguidebook/thetradingwindow/position_and_p___l.htm
#########################################################

class AbstractPosition(object):
    """
    The Position abstract class handles
    each underlying bookeeping
    A unique interface for all instruments:
    shares, futures, ...

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update_value(self, bid, ask):
        """
        Market value estimated via the mid-price of the
        bid-ask spread, incl calculation of the unrealised
        and realised profit & loss.
        """
        raise NotImplementedError("Should implement update_value()")

    @abstractmethod
    def trade(self, order_type, quantity, price, commission):
        """
        Calculates the adjustments to Position
        once units/lots are addes/reduced.

        Updates the average bought/sold, total
        bought/sold, the cost and PnL calculations.
        """
        raise NotImplementedError("Should implement trade()")
