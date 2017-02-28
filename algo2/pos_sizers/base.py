# no shebang
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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

