from nose.tools import assert_equal, assert_false, assert_raises, assert_true

import datetime
from decimal import Decimal # NB: use of Decimal here vs. none in portfolio_tests


from Algo2.event import FillEvent, OrderEvent, SignalEvent
from Algo2.portfolio_handler import PortfolioHandler
from Algo2.feed import AbstractTickDataHandler
from Algo2.utilities import queue


#   create mock objects for data handler, position sizer and risk mgt
#
class DataHandlerMock(AbstractTickDataHandler):
    # fnct below is to define 'tickers'
    def get_best_bid_ask(self, ticker):
        prices = {
            "MSFT": (Decimal("50.28"), Decimal("50.31")),
            "GOOG": (Decimal("705.46"), Decimal("705.46")),
            "AMZN": (Decimal("564.14"), Decimal("565.14")),
        }
        return prices[ticker]

class PositionSizerMock(object):
    def size_order(self, portfolio, initial_order):
        """
        This PositionSizerMock object simply modifies
        the quantity to be 100 of any share transacted.
        """
        initial_order.quantity = 100    # modify the qnty
        return initial_order            # return order

class RiskManagerMock(object):
    def __init__(self):
        pass

    def refine_orders(self, portfolio, sized_order):
        """
        This RiskManagerMock object simply lets the
        sized order through, creates the corresponding
        OrderEvent object and adds it to a list.
        """
        order_event = OrderEvent(
            sized_order.ticker,
            sized_order.action,
            sized_order.quantity
        )
        return [order_event]


#   test whole cycle
def test_simple_Signal_Order_Fill_cycle_x_PortfolioHandler():
    """
    Tests a simple Signal, Order and Fill cycle for the
    PortfolioHandler.
    """

    # Set up the PortfolioHandler object
    initial_cash = Decimal("500000.00")
    events_queue = queue.Queue()
    data_handler = DataHandlerMock()
    position_sizer = PositionSizerMock() # initial_order = 100
    risk_manager = RiskManagerMock()

    portfolio_handler = PortfolioHandler(
            initial_cash, events_queue, data_handler,
            position_sizer, risk_manager
    )

    # sanity check '_create_order_from_signal'
    signal_event = SignalEvent("MSFT", "BOT")
    order_from = portfolio_handler._create_order_from_signal(signal_event)
    assert_equal(order_from.ticker, "MSFT")
    assert_equal(order_from.action, "BOT")
    assert_equal(order_from.quantity, 0) # <-

    # sanity check '_place_orders_onto_queue' method
    order = OrderEvent("MSFT", "BOT", 100)
    order_list = [order]
    portfolio_handler._place_orders_onto_queue(order_list)
    ret_order = portfolio_handler.events_queue.get()  # <---
    assert_equal(ret_order.ticker, "MSFT")
    assert_equal(ret_order.action, "BOT")
    assert_equal(ret_order.quantity, 100)

    # check "on_signal" method
    signal_event = SignalEvent("MSFT", "BOT")
    portfolio_handler.on_signal(signal_event)
    ret_order = portfolio_handler.events_queue.get()
    assert_equal(ret_order.ticker, "MSFT")
    assert_equal(ret_order.action, "BOT")
    assert_equal(ret_order.quantity, 100)  # <-

    # check "on_fill" method
    fill_event_buy = FillEvent(
            datetime.datetime.utcnow(), "MSFT", "BOT",
            100, "FakeExchange", Decimal("50.25"), Decimal("1.00")
    )
    portfolio_handler.on_fill(fill_event_buy)
    # Check the Portfolio values within the PortfolioHandler
    port = portfolio_handler.portfolio
    assert_equal(port.cur_cash, Decimal("494974.00"))

    # TODO: Finish this off and check it works via Interactive Brokers
    fill_event_sell = FillEvent(
            datetime.datetime.utcnow(), "MSFT", "SLD",
            100, "ARCA", Decimal("50.25"), Decimal("1.00")
    )
    portfolio_handler.on_fill(fill_event_sell)



