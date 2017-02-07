from .base_refiner import AbstractPositionRefiner
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
