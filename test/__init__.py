# -*- coding: utf-8 -*-

# Copyright (c) 2013-2015 Matthew Zipay <mattz@ninthtest.net>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Utility functions and classes for all unit test modules."""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.4.0"

from functools import partial
import logging
import os
import unittest

from autologging import TRACE

__all__ = [
    "dummy_module_logger",
    "dummy2_module_logger",
    "dummy3_module_logger",
    "get_dummy_lineno",
    "get_dummy2_lineno",
    "get_dummy3_lineno",
    "list_handler",
    "named_logger",
    "named_tracer",
    "suite",
]


def _get_lineno(relfn, marker):
    fn = os.path.join(os.path.dirname(_get_lineno.__code__.co_filename), relfn)
    with open(fn) as fp:
        for (i, line) in enumerate(fp):
            if (marker in line):
                return i + 1


get_dummy_lineno = partial(_get_lineno, "dummy.py")
get_dummy2_lineno = partial(_get_lineno, "_dummy2.py")
get_dummy3_lineno = partial(_get_lineno, "_dummy3.py")


class _ListHandler(logging.Handler):
    """Store log records in the order in which they are emitted."""

    def __init__(self, *args, **keywords):
        super(_ListHandler, self).__init__(*args, **keywords)
        self.reset()

    records = property(lambda self: self._records)

    def emit(self, record):
        self._records.append(record)

    def reset(self):
        self._records = []


# set up all test logging ahead of time so that the tracing logger proxies
# behave correctly
# (this is a not a testing-specific approach... an application should have its
# logging configuration in place ahead of time as well)
list_handler = _ListHandler(level=TRACE)

dummy_module_logger = logging.getLogger("test.dummy")
dummy_module_logger.addHandler(list_handler)

dummy2_module_logger = logging.getLogger("test._dummy2")
dummy2_module_logger.addHandler(list_handler)

dummy3_module_logger = logging.getLogger("test._dummy3")
dummy3_module_logger.addHandler(list_handler)

named_logger = logging.getLogger("logged.testing")
named_logger.setLevel(logging.INFO)
named_logger.addHandler(list_handler)

named_tracer = logging.getLogger("traced.testing")
named_tracer.setLevel(TRACE)
named_tracer.addHandler(list_handler)


def suite():
    from test import (
        test_autologging,
        test_logged,
        test_traced,
        test_TracedMethods,
    )

    suite = unittest.TestSuite()
    suite.addTest(test_autologging.suite())
    suite.addTest(test_logged.suite())
    suite.addTest(test_traced.suite())
    suite.addTest(test_TracedMethods.suite())

    return suite

