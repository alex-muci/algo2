# import click

from Algo2 import utilities
from Algo2.utilities import queue
from Algo2.feeds.csv_files import HistoricCSVBarDataHandler

from Algo2.strategies.buy_and_hold import BuyAndHoldStrategy, NEWBuyAndHoldStrategyNEW
# from Algo2.strategies.display import DisplayStrategy    # for comparison
# from Algo2.strategies.base_strategy import Strategies   # wrapper of two stategies

from Algo2.pos_sizers.naive import FixedPositionSizer       # used in portfolio_handler
from Algo2.pos_refiners.naive import NaivePositionRefiner   # used in portfolio_handler
from Algo2.portfolio_handler import PortfolioHandler

from Algo2.brokers.simulated_broker import IBSimulatedExecutionHandler
from Algo2.statistics.simple import SimpleStatistics
from Algo2.backtest import Backtest


# wrapping all up, easier for automatize test
def run(config, testing, tickers, filename):

    # Set up variables for backtest()
    events_queue = queue.Queue()
    csv_dir = config.CSV_DATA_DIR
    initial_equity = 500000.00

    # Use historic (Yahoo Daily) data handler
    data_handler = HistoricCSVBarDataHandler(csv_dir, events_queue, tickers)

    # Use the Buy-and-Hold Strategy
    strategy = BuyAndHoldStrategy(tickers, events_queue)
    # strategy = Strategies(strategy, DisplayStrategy())    # UN-COMMENT

    # Use an example Position Sizer and Refiner (risk mgt)
    position_sizer = FixedPositionSizer()   # i.e. NaiveStockPosSizer(100)
    position_refiner = NaivePositionRefiner()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        initial_equity, events_queue, data_handler,
        position_sizer, position_refiner
    )

    # Accounting object?

    # Use a simulated IB Execution Handler
    broker_handler = IBSimulatedExecutionHandler(events_queue, data_handler)    # , compliance)

    # Use the default Statistics
    statistics = SimpleStatistics(config, portfolio_handler)

    # Set up the backtest
    backtest = Backtest(
        data_handler, strategy,
        portfolio_handler, broker_handler,
        position_sizer, position_refiner,
        statistics, initial_equity
    )
    results = backtest.simulate_trading(testing=testing)
    statistics.save(filename, False)    # if True: also saves a .csv file with main curves
    return results


##############################################
def main():
    config = utilities.DEFAULT
    testing = False
    tickers = ['SP500TR']  # ; tickers = tickers.split(",")
    filename = ""
    run(config, testing, tickers, filename)


#########################################################
if __name__ == "__main__":
    main()
