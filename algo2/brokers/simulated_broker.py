#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from algo2.brokers.base_broker import AbstractBroker
from algo2.event import FillEvent, EventType


class IBSimulatedExecutionHandler(AbstractBroker):
    """
    The simulated execution handler for Interactive Brokers
    converts all order objects into their equivalent fill
    objects automatically without latency, slippage or
    fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """

    def __init__(self, events_queue, data_handler):
        """
        Initialises the handler, setting the event queue
        as well as access to local pricing.
        """
        self.events_queue = events_queue
        self.data_handler = data_handler
    #   self.compliance = compliance

    @staticmethod
    def calculate_ib_commission(quantity, fill_price):
        """
        Calculate the Interactive Brokers commission
        https://www.interactivebrokers.co.uk/en/index.php?f=1590&p=stocks1
        """
        commission = min(
            0.5 * fill_price * quantity,
            max(1.0, 0.005 * quantity)
        )
        return commission

    def execute_order(self, event):
        """
        Converts OrderEvents into FillEvents "naively",
        i.e. without any latency, slippage or fill ratio problems.

        :param event - an Event object with order information.
        """
        if event.type == EventType.ORDER:
            # Obtain values from the OrderEvent
            timestamp = self.data_handler.get_last_timestamp(event.ticker)
            ticker = event.ticker
            action = event.action
            quantity = event.quantity

            # Obtain price from data_handler feed
            if self.data_handler.istick():
                bid, ask = self.data_handler.get_best_bid_ask(ticker)
                if event.action == "BOT":
                    fill_price = ask
                else:
                    fill_price = bid
            else:
                close_price = self.data_handler.get_last_adjclose(ticker)
                fill_price = close_price

            # Set a dummy exchange and calculate trade commission
            exchange = "SimulatedMkt"
            commission = self.calculate_ib_commission(quantity, fill_price)

            # Create the FillEvent and place on the events queue
            fill_event = FillEvent(
                timestamp, ticker,
                action, quantity,
                exchange, fill_price,
                commission
            )
            self.events_queue.put(fill_event)

        # if self.compliance is not None:
        #   self.compliance.record_trade(fill_event)
