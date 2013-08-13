# -*- coding: utf-8 -*-

# Copyright (c) 2013 Matthew Zipay <mattz@ninthtest.net>
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
__version__ = "0.1"

from functools import wraps
import logging
import sys
import unittest

__all__ = [
    "ListHandler",
    "load_tests",
    "skip_if",
]

try:
    skip_if = unittest.skipIf
except AttributeError:
    # unittest.skipIf is not available in all versions of Python
    def skip_if(condition, reason):
        if (condition):
            def decorator(test_obj):
                @wraps(test_obj)
                def skip_wrapper(*args, **kwargs):
                    sys.stderr.write("\nSKIPPED %s (%s)\n" %
                                     (test_obj.__name__, reason))
                return skip_wrapper
            return decorator
        else:
            return lambda obj: obj


class ListHandler(logging.Handler):
    """Store log records in the order in which they are emitted."""

    def __init__(self, *args, **keywords):
        super(ListHandler, self).__init__(*args, **keywords)
        self._records = []

    records = property(lambda self: self._records)

    def emit(self, record):
        self._records.append(record)


def suite():
    from test import test_logged, test_logged_functions, test_traced, test_TracedMethods
    suite = unittest.TestSuite()
    suite.addTest(test_logged.suite())
    suite.addTest(test_logged_functions.suite())
    suite.addTest(test_traced.suite())
    suite.addTest(test_TracedMethods.suite())
    return suite
