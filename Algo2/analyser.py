from abc import ABCMeta, abstractmethod
from utilities import pickle


class AbstractAnalyser(object):
    """
    Analyser is an abstract class providing an interface for
    all inherited statistic classes (live, historic, custom, etc).

    The goal of this object is to keep a record of statistical info
    about trading strategies byy hooking into the event loop
    and updating the object according to portfolio performance.

    Ideally, Analyser should be subclassed according to the strategies
    and timeframes traded by the user. Different trading strategies
    may require different metrics or frequencies-of-metrics to be updated.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, timestamp, portfolio_handler):
        """
        Update all the statistics according to values of the portfolio
        and open positions.
        This should be called from within the event loop.
        """
        raise NotImplementedError("Should implement update()")

    @abstractmethod
    def get_results(self):
        """
        Return a dict containing all statistics.
        """
        raise NotImplementedError("Should implement get_results()")

    @abstractmethod
    def plot_results(self):
        """
        Plot all statistics collected up until 'now'
        """
        raise NotImplementedError("Should implement plot_results()")

    @abstractmethod
    def save(self, filename):
        """
        Save statistics results to filename
        """
        raise NotImplementedError("Should implement save()")

    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as fd:
            stats = pickle.load(fd)
        return stats


# # # # # # # # # #
def load(filename):
    return AbstractAnalyser.load(filename)
