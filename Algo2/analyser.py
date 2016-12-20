#!/usr/bin/python
# -*- coding: utf-8  -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
import numpy as np
from itertools import groupby


def get_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a 
    benchmark of zero (i.e. no risk-free rate information).

    Parameters:
    returns - A pandas Series representing period percentage returns.
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """
    years = len(returns) / float(periods) 
    one_plus_cumrtrn = np.exp( np.sum(np.log(1 + returns)) )  
    
    ann_rtrn = (one_plus_cumrtrn ** (1.0 / years)) - 1.0  # ann_rtrn = np.mean(returns) * periods  # approx
    
    sharpe = np.sqrt(periods) * (np.mean(returns)) / np.std(returns)
    
    return sharpe, ann_rtrn

########################################
def get_drawdowns(returns):
    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the 
    pnl_returns is a pandas Series.

    Parameters:
    returns - A pandas Series representing period percentage returns.

    Returns:
    drawdown, duration - Highest peak-to-trough drawdown and duration.
    """
    # set up 
    idx = returns.index; _len = len(idx) #cdef double[:] 
    hwm = np.zeros(_len) # was: hwm = [0]
    drawdown = np.zeros(_len) #drawdown = pd.Series(index = idx) # VERY SLOW IN LOOP BELOW
    duration = np.zeros(_len) #duration = pd.Series(index = idx) # VERY SLOW IN LOOP BELOW
        
    
    # Loop over the index range
    for t in xrange(1, _len):
        hwm[t] = max(hwm[t-1], returns[t]) #    was:  hwm.append(max(hwm[t-1], returns[t]))
        drawdown[t] = (returns[t] - hwm[t]) 
        duration[t] = (0 if drawdown[t] == 0 else duration[t-1]+1)
    
    return drawdown, drawdown.min(), duration.max()


"""    # with percentage inputs:
        highwatermark[t]=np.max( [highwatermark[t-1], cumret[t]] )
        drawdown[t]=(1+cumret[t])/(1+highwatermark[t])-1
"""
#####################################
# FROM QS_TRADER, 6x faster
#####################################
def get_drawdowns_2v(returns):
    """
    Calculate the largest peak-to-trough drawdown of the equity curve
    as well as the duration of the drawdown. Requires that the
    pnl_returns is a pandas Series.
    Parameters:
    returns - A pandas Series representing period percentage returns.
    Returns:
    drawdown, drawdown_max, duration
    """
    # Calculate the cumulative returns curve
    # and set up the High Water Mark
    idx = returns.index
    hwm = np.zeros(len(idx))

    # Create the high water mark
    for t in range(1, len(idx)):
        hwm[t] = max(hwm[t - 1], returns.ix[t])

    # Calculate the drawdown and duration statistics
    perf = pd.DataFrame(index=idx)
    perf["Drawdown"] = (returns - hwm) / hwm; perf["Drawdown"].ix[0] = 0.0
    perf["DurationCheck"] = np.where(perf["Drawdown"] == 0, 0, 1)
    duration = max( sum(1 for i in g if i == 1)
                    for _ , g in groupby(perf["DurationCheck"])  )
    
    return perf["Drawdown"], np.min(perf["Drawdown"]), duration


#####################################
# max drawdown: in O(n) rather than O(n^2) time
#####################################
def max_dd(returns):
    max2here = pd.expanding_max(returns) 
    dd = returns - max2here
    return dd.min()

