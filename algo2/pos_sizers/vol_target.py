#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from algo2.pos_sizers.base_sizer import AbstractPositionSizer   # using absolute ref


class VolTargetStockPositionSizer(AbstractPositionSizer):
    """
    Carries out a volatility target sizing
    for a Stock the order.
    """
    def size_order(self, portfolio, initial_order):

        pass
