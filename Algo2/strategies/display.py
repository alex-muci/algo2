#!/usr/bin/env/python

import time

from Algo2.strategy import AbstractStrategy
from Algo2.event import EventType


######################
# auxiliary functions
def speed(ticks, t0):
    return ticks / (time.time() - t0)


def s_speed(time_event, ticks, t0):
    sp = speed(ticks, t0)
    s_typ = time_event.typename + "S"
    return "%d %s processed @ %f %s/s" % (ticks, s_typ, sp, s_typ)


######################
class DisplayStrategy(AbstractStrategy):
    """
    A strategy displaying ticks / bars

    :param
        n = 100
        n_window = 5
    """

    def __init__(self, n=100, n_window=5):
        self.n = n
        self.n_window = n_window
        self.t0 = time.time()
        self.i = 0

    def calculate_signals(self, event):
        if event.type in [EventType.TICK, EventType.BAR]:
            if self.i % self.n == 0 and self.i != 0:
                print(s_speed(event, self.i, self.t0))
                print("")
            if self.i % self.n in range(self.n_window):
                print("%d %s" % (self.i, event))
            self.i += 1
