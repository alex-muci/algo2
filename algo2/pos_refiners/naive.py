# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from algo2.pos_refiners.base_refiner import AbstractPositionRefiner
from algo2.event import OrderEvent


class NaivePositionRefiner(AbstractPositionRefiner):
    def refine_orders(self, portfolio, sized_order):
        """
        The NaivePositionRefiner simply lets the
        sized order through: (i) creates the corresponding
        OrderEvent and (ii) adds it to a list.
        """
        order_event = OrderEvent(
            sized_order.ticker,
            sized_order.action,
            sized_order.quantity
        )
        return [order_event]
