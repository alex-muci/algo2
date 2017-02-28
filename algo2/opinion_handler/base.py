# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from abc import ABCMeta, abstractmethod


class AbstractOpinionHandler(object):
    """
    AbstractOpinionHandler is an abstract base class providing
    an interface for all inherited opinion handlers .
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def stream_next(self, stream_date=None):
        """
        Interface method for streaming the next OpinionEvent
        object to the events queue.
        """
        raise NotImplementedError("stream_next is not implemented in the base class!")