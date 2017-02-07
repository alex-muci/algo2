from nose.tools import assert_equal
from algo2.positions.stock import Stock

# TODO: futures test below

def test_calculate_futures_round_trip():
    """
    Test a round-trip trade in one futures contract.
    """
    pass



def test_calculate_stock_round_trip():
    """
    Test a round-trip trade in Exxon-Mobil 'XOM'.    
    
    The following prices have been tested against those calculated
    via Interactive Brokers' Trader Workstation (TWS).
    """
    
    # set position with a buy
    XOM_position = Stock("BOT", "XOM",  # order_type, symbol,
                        100, 74.78, 1.00,  #init_quantity, init_price, init_commission,
                        74.78, 74.80  # bid, ask
                         )
    #  execute a few more trades     #:input: order_type, quantity, price, commission
    XOM_position.trade("BOT", 100, 74.63, 1.0)
    XOM_position.trade("BOT", 250, 74.620, 1.25)    
    XOM_position.trade("SLD", 200, 74.58, 1.00)    
    XOM_position.trade("SLD", 250, 75.26, 1.25)
    
    # update mkt value    # :inputs: bid, ask
    XOM_position.update_value(77.75, 77.77)

    # checks
    assert_equal(XOM_position.order_type, "BOT")
    assert_equal(XOM_position.symbol, "XOM")
    
    assert_equal(XOM_position.quantity, 0) # final qnty after round-trip
    assert_equal(XOM_position.buys, 450)
    assert_equal(XOM_position.sells, 450)
    assert_equal(XOM_position.net, 0)
    
    assert_equal(round(XOM_position.avg_bot, 5), 74.65778)
    assert_equal(round(XOM_position.avg_sld, 5), 74.95778)
    
    assert_equal(XOM_position.total_bot, 33596.00)
    assert_equal(XOM_position.total_sld, 33731.00)
    assert_equal(XOM_position.net_total, 135.00)
    assert_equal(XOM_position.total_commission, 5.50)
    assert_equal(XOM_position.net_incl_comm, 129.50)
    
    assert_equal(round(XOM_position.avg_price, 3), 74.665)
    assert_equal(XOM_position.cost, 0.00)
    
    assert_equal(XOM_position.market_value, 0.00)
    assert_equal(XOM_position.unrealised_pnl, 0.00)
    assert_equal(XOM_position.realised_pnl, 129.50)
