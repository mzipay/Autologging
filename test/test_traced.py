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

"""Test cases and runner for the :func:`autologging.traced` decorator
function.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.4.0"

import logging
import os
import sys
from types import FunctionType
import unittest

from autologging import TRACE
from test import dummy_module_logger, get_dummy_lineno, list_handler
from test.dummy import traced_function

_ge_py33 = ((sys.version_info[0] == 3) and (sys.version_info[1] >= 3))

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class TracedDecoratorTest(unittest.TestCase):
    """Test the :func:`autologging.traced` decorator."""

    @classmethod
    def setUpClass(cls):
        dummy_module_logger.setLevel(TRACE)

    def setUp(self):
        list_handler.reset()

    def test_traced_sets_correct_function_logger(self):
        # the logger delegators are free variable of the tracing proxy function
        # closures
        var_index = \
            traced_function.__code__.co_freevars.index("logger_delegator")
        logger_delegator = traced_function.__closure__[var_index].cell_contents
        self.assertEqual("test.dummy", logger_delegator.name)
        self.assertEqual(TRACE, logger_delegator.getEffectiveLevel())

        nested_function = traced_function(None)
        var_index = \
            nested_function.__code__.co_freevars.index("logger_delegator")
        logger_delegator = nested_function.__closure__[var_index].cell_contents
        self.assertEqual("traced.testing", logger_delegator.name)
        self.assertEqual(TRACE, logger_delegator.level)

    def test_traced_function_returns_expected_result(self):
        return_value = traced_function(None)
        self.assertTrue(type(return_value) is FunctionType)
        self.assertEqual("nested_function", return_value.__name__)

    def test_traced_function_log_records_are_accurate(self):
        nested_function = traced_function("spam", keyword="eggs")
        nested_function_addr = hex(id(nested_function))
        self.assertEqual(2, len(list_handler.records))

        return_record = list_handler.records.pop()
        self.assertEqual("test.dummy", return_record.name)
        self.assertEqual("traced_function", return_record.funcName)
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertTrue(return_record.pathname.endswith("test/dummy.py"))
        self.assertEqual(
            "RETURN <function traced_function.<locals>.nested_function at %s>" %
                    nested_function_addr
                if _ge_py33 else "RETURN <function nested_function at %s>" %
                    nested_function_addr,
            return_record.getMessage())
        self.assertEqual(get_dummy_lineno("#t_f:LN"), return_record.lineno)

        call_record = list_handler.records.pop()
        self.assertEqual("test.dummy", call_record.name)
        self.assertEqual("traced_function", call_record.funcName)
        self.assertEqual("TRACE", call_record.levelname)
        self.assertEqual(TRACE, call_record.levelno)
        self.assertTrue(call_record.pathname.endswith("test/dummy.py"))
        self.assertEqual("CALL *('spam',) **{'keyword': 'eggs'}",
                         call_record.getMessage())
        self.assertEqual(get_dummy_lineno("#t_f:L1"), call_record.lineno)

    def test_nested_function_returns_expected_result(self):
        nested_function = traced_function("spam", keyword="eggs")
        self.assertEqual("spam and eggs", nested_function())

    def test_nested_function_log_records_are_accurate(self):
        nested_function = traced_function("spam", keyword="eggs")

        # discard the traced_function records
        list_handler.reset()

        nested_function()
        self.assertEqual(2, len(list_handler.records))

        return_record = list_handler.records.pop()
        self.assertEqual("traced.testing", return_record.name)
        self.assertEqual("nested_function", return_record.funcName)
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertTrue(return_record.pathname.endswith("test/dummy.py"))
        self.assertEqual("RETURN 'spam and eggs'",
                         return_record.getMessage())
        self.assertEqual(get_dummy_lineno("#n_f:LN"), return_record.lineno)

        call_record = list_handler.records.pop()
        self.assertEqual("traced.testing", call_record.name)
        self.assertEqual("nested_function", call_record.funcName)
        self.assertEqual("TRACE", call_record.levelname)
        self.assertEqual(TRACE, call_record.levelno)
        self.assertTrue(call_record.pathname.endswith("test/dummy.py"))
        self.assertEqual("CALL *() **{}",
                         call_record.getMessage())
        self.assertEqual(get_dummy_lineno("#n_f:L1"), call_record.lineno)


def suite():
    """Build the test suite for :func:`autologging.traced`."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TracedDecoratorTest))
    return suite


if (__name__ == "__main__"):
    unittest.TextTestRunner().run(suite())

