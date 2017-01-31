from nose.tools import assert_equal, assert_raises, assert_true
import os

from Algo2.feeds.csv_files import HistoricCSVTickDataHandler
import Algo2.utilities as utils
from Algo2.utilities import queue


# TODO: complete other function for BAR

def test_HistoricCVSBar():
    pass


def test_HistoricCSVTick():
    """
    Test Tick DataHandler object with 3 tickers:
    - check initialisation,
    - check subscription,
    - check get_best_bid_ask,
    - stream subsequent ticks and check correct bid-ask returned,
    - check un-subscription.
    """
    #################################
    # set up 3 initial tickers.
    # algo2_dir = os.path.dirname(os.path.dirname(__file__)); csv_path = os.path.join(algo2_dir, 'data')
    csv_path = utils.DEFAULT.CSV_DATA_DIR
    events_queue = queue.Queue()
    init_tickers = ["GOOG", "AMZN", "MSFT"]
    price_handler = HistoricCSVTickDataHandler(
        csv_path, events_queue, init_tickers
        )
    # __init__ opens three CSV files, merge and sort them
    # then be stored in a member "tick_stream".

    #################################
    # Check a ticker that is already subscribed
    try:
        price_handler.subscribe_ticker("GOOG")
    except Exception as E:
        assert_raises("subscribe_ticker() raised %s unexpectedly" % E)

    #################################
    # Tests 'get_best_bid_ask' method (top price)
    # before calling stream_next
    bid, ask = price_handler.get_best_bid_ask("AMZN")
    assert_equal(round(bid, 5), 502.10001)
    assert_equal(round(ask, 5), 502.11999)

    #################################
    # Stream to Tick #1 (GOOG)
    price_handler.stream_next()
    assert_equal(price_handler.tickers["GOOG"]["timestamp"].strftime("%d-%m-%Y %H:%M:%S.%f"),
            "01-02-2016 00:00:01.358000")
    assert_equal(round(price_handler.tickers["GOOG"]["bid"], 5), 683.56000 )
    assert_equal(round(price_handler.tickers["GOOG"]["ask"], 5), 683.58000)

    # Stream to Tick #2 (AMZN)
    price_handler.stream_next()
    assert_equal(price_handler.tickers["AMZN"]["timestamp"].strftime("%d-%m-%Y %H:%M:%S.%f"),
            "01-02-2016 00:00:01.562000")
    assert_equal(round(price_handler.tickers["AMZN"]["bid"], 5), 502.10001)
    assert_equal(round(price_handler.tickers["AMZN"]["ask"], 5), 502.11999)

    # Stream to Tick #3 (MSFT)
    price_handler.stream_next()
    assert_equal(price_handler.tickers["MSFT"]["timestamp"].strftime("%d-%m-%Y %H:%M:%S.%f" ),
            "01-02-2016 00:00:01.578000" )
    assert_equal(round(price_handler.tickers["MSFT"]["bid"], 5), 50.14999)
    assert_equal(round(price_handler.tickers["MSFT"]["ask"], 5), 50.17001)

    # Stream to Tick #10 (GOOG)
    for i in range(4, 11):
        price_handler.stream_next()
    assert_equal(price_handler.tickers["GOOG"]["timestamp"].strftime("%d-%m-%Y %H:%M:%S.%f"),
            "01-02-2016 00:00:05.215000")
    assert_equal(round(price_handler.tickers["GOOG"]["bid"], 5), 683.56001)
    assert_equal(round(price_handler.tickers["GOOG"]["ask"], 5), 683.57999)

    # Stream to Tick #20 (GOOG)
    for i in range(11, 21):
        price_handler.stream_next()
    # check
    assert_equal(price_handler.tickers["MSFT"]["timestamp"].strftime("%d-%m-%Y %H:%M:%S.%f"),
            "01-02-2016 00:00:09.904000")
    assert_equal(round(price_handler.tickers["MSFT"]["bid"], 5), 50.15000)
    assert_equal(round(price_handler.tickers["MSFT"]["ask"], 5), 50.17000)

    #################################
    # Unsubscribe a current ticker
    price_handler.unsubscribe_ticker("GOOG")
    assert_true("GOOG" not in price_handler.tickers)
    assert_true("GOOG" not in price_handler.tickers_data)
