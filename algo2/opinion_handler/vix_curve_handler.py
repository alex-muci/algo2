# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import pandas as pd

from algo2.opinion_handler.base import AbstractOpinionHandler
from algo2.event import OpinionEvent


class VixOpinionHandler(AbstractOpinionHandler):
    """
    VixOpinionHandler is designed to provide a backtesting
    opnion handler for VIX and VIXX indices.
    """
    def __init__(
        self, csv_dir, filename,
        events_queue,  # tickers=None,
        start_date=None, end_date=None
    ):
        self.csv_dir = csv_dir
        self.filename = filename

        self.events_queue = events_queue
        # self.tickers = tickers

        self.start_date = start_date
        self.end_date = end_date

        self.sent_df = self._open_opinion_csv()
        self.sent_df_stream = self.sent_df.iterrows()

    def _open_opinion_csv(self):
        """
        Opens the CSV file containing the VIX index info
        and places it into a pandas DataFrame.
        """
        opinion_path = os.path.join(self.csv_dir, self.filename)
        sent_df = pd.read_csv(
            opinion_path, parse_dates=True,
            header=0, index_col=0, dayfirst=True,
            # names=("Date", "VIX", "VXX", ..., VIX30, ...)
        )
        if self.start_date is not None:
            sent_df = sent_df[self.start_date.strftime("%Y-%m-%d"):]
        if self.end_date is not None:
            sent_df = sent_df[:self.end_date.strftime("%Y-%m-%d")]
        if self.tickers is not None:
            sent_df = sent_df[sent_df["Ticker"].isin(self.tickers)]
        return sent_df

    def stream_next(self, stream_date=None):
        """
        Stream the next VIX values.
        """
        if stream_date is None:
            try:
                index, row = next(self.sent_df_stream)
            except StopIteration:
                # self.continue_backtest = False
                return
            oev = OpinionEvent(stream_date, row["VIX"], row["VXX"])
            self.events_queue.put(oev)

        else:   # stream_date is not None   #TODO: check if necessary 'else' block below
            stream_date_str = stream_date.strftime("%Y-%m-%d")   # to use 'ix' as per 'loc', i.e. by label
            date_df = self.sent_df.ix[stream_date_str:stream_date_str]
            for row in date_df.iterrows():
                sev = OpinionEvent(stream_date, row[1]["VIX"], row[1]["VXX"])
                self.events_queue.put(sev)
