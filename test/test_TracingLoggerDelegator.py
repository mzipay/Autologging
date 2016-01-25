# -*- coding: utf-8 -*-

# Copyright (c) 2013-2016 Matthew Zipay <mattz@ninthtest.net>
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

"""Test case and runner for
:func:`autologging._create_log_record_factories`.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"

import logging
import unittest

from autologging import TRACE, _TracingLoggerDelegator, __version__

from test import has_co_lnotab, is_ironpython, list_handler

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


def sample_function(arg, keyword=None):
    x = arg.upper()
    return "%s %s" % (arg, keyword)


_expected_function_filename = sample_function.__code__.co_filename
_expected_function_firstlineno = 41
_expected_function_lastlineno = 43 if has_co_lnotab else 41


class SampleClass(object):
    
    def method(self, arg, keyword=None):
        x = arg.upper()
        return "%s %s" % (arg, keyword)


_method = SampleClass.__dict__["method"]
_expected_method_filename = _method.__code__.co_filename
_expected_method_firstlineno = 53
_expected_method_lastlineno = 55 if has_co_lnotab else 53

_module_logger = logging.getLogger(__name__)
_module_logger.setLevel(TRACE)
_module_logger.addHandler(list_handler)

_class_logger = logging.getLogger(__name__ + ".SampleClass")
_class_logger.propagate = False
_class_logger.setLevel(TRACE)
_class_logger.addHandler(list_handler)


class TracingLoggerDelegatorTest(unittest.TestCase):
    """Test the :class:`autologging._TracingLoggerDelegator` class."""

    @classmethod
    def setUpClass(cls):
        cls._function_delegator = _TracingLoggerDelegator(
            _module_logger, sample_function)
        cls._method_delegator = _TracingLoggerDelegator(_class_logger, _method)

    def setUp(self):
        list_handler.reset()

    def test_find_last_line_number_of_function(self):
        self.assertEqual(
            _expected_function_lastlineno,
            _TracingLoggerDelegator._find_last_line_number(
                sample_function.__code__))

    def test_find_last_line_number_of_method(self):
        self.assertEqual(
            _expected_method_lastlineno,
            _TracingLoggerDelegator._find_last_line_number(_method.__code__))

    def test_init_sets_expected_log_record_attributes_for_function(self):
        self.assertEqual(
            _expected_function_filename,
            self._function_delegator._f_filename)
        self.assertEqual(
            _expected_function_firstlineno,
            self._function_delegator._f_firstlineno)
        self.assertEqual(
            _expected_function_lastlineno,
            self._function_delegator._f_lastlineno)
        self.assertEqual(
            "sample_function", self._function_delegator._f_name)

    def test_init_sets_expected_log_record_attributes_for_method(self):
        self.assertEqual(
            _expected_method_filename, self._method_delegator._f_filename)
        self.assertEqual(
            _expected_method_firstlineno,
            self._method_delegator._f_firstlineno)
        self.assertEqual(
            _expected_method_lastlineno, self._method_delegator._f_lastlineno)
        self.assertEqual("method", self._method_delegator._f_name)

    def test_reports_expected_logger_name(self):
        self.assertEqual(_module_logger.name, self._function_delegator.name)
        self.assertEqual(_class_logger.name, self._method_delegator.name)

    def test_delegator_name_is_readonly(self):
        self.assertRaises(
            AttributeError,
            setattr, self._method_delegator, "name", "this.should.fail")

    def test_reports_expected_logger_propagate(self):
        self.assertFalse(self._method_delegator.propagate)
        _class_logger.propagate = True
        self.assertTrue(self._method_delegator.propagate)
        # reset
        _class_logger.propagate = False

    def test_delegator_propagate_is_readonly(self):
        self.assertRaises(
            AttributeError,
            setattr, self._method_delegator, "propagate", True)

    def test_reports_expected_enabled_for_level(self):
        self.assertTrue(self._method_delegator.isEnabledFor(TRACE))
        _class_logger.setLevel(logging.FATAL)
        self.assertFalse(self._method_delegator.isEnabledFor(logging.INFO))
        # reset
        _class_logger.setLevel(TRACE)

    def test_reports_expected_effective_level(self):
        self.assertEqual(TRACE, self._method_delegator.getEffectiveLevel())
        _class_logger.setLevel(logging.NOTSET)
        # should still report TRACE (module logger is the immediate parent)
        self.assertEqual(TRACE, self._method_delegator.getEffectiveLevel())
        # reset
        _class_logger.setLevel(TRACE)

    def test_reports_expected_handlers(self):
        self.assertTrue(self._method_delegator.hasHandlers())
        _class_logger.removeHandler(list_handler)
        self.assertFalse(self._method_delegator.hasHandlers())
        _class_logger.propagate = True
        # NOW it should report True (will propagate to _module_logger, which
        # has list_handler)
        self.assertTrue(self._method_delegator.hasHandlers())
        # reset
        _class_logger.addHandler(list_handler)
        _class_logger.propagate = False

    def test_trace_function_call(self):
        f_args = ("spam",)
        f_keywords = dict(keyword="eggs")
        self._function_delegator.trace_call(f_args, f_keywords)

        self.assertEqual(1, len(list_handler.records))

        call_record = list_handler.records[0]
        self.assertEqual(_module_logger.name, call_record.name)
        self.assertEqual("CALL *%r **%r", call_record.msg)
        self.assertEqual((f_args, f_keywords), call_record.args)
        self.assertEqual("TRACE", call_record.levelname)
        self.assertEqual(TRACE, call_record.levelno)
        self.assertEqual(_expected_function_filename, call_record.pathname)
        self.assertEqual(_expected_function_firstlineno, call_record.lineno)
        self.assertEqual("sample_function", call_record.funcName)

    def test_trace_function_return(self):
        f_return = "SPAM eggs"
        self._function_delegator.trace_return(f_return)

        self.assertEqual(1, len(list_handler.records))

        return_record = list_handler.records[0]
        self.assertEqual(_module_logger.name, return_record.name)
        self.assertEqual("RETURN %r", return_record.msg)
        self.assertEqual((f_return,), return_record.args)
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertEqual(_expected_function_filename, return_record.pathname)
        self.assertEqual(_expected_function_lastlineno, return_record.lineno)
        self.assertEqual("sample_function", return_record.funcName)

    def test_trace_method_call(self):
        f_args = ("spam",)
        f_keywords = dict(keyword="eggs")
        self._method_delegator.trace_call(f_args, f_keywords)

        self.assertEqual(
            1, len(list_handler.records), repr(list_handler.records))

        call_record = list_handler.records[0]
        self.assertEqual(_class_logger.name, call_record.name)
        self.assertEqual("CALL *%r **%r", call_record.msg)
        self.assertEqual((f_args, f_keywords), call_record.args)
        self.assertEqual("TRACE", call_record.levelname)
        self.assertEqual(TRACE, call_record.levelno)
        self.assertEqual(_expected_method_filename, call_record.pathname)
        self.assertEqual(_expected_method_firstlineno, call_record.lineno)
        self.assertEqual("method", call_record.funcName)

    def test_trace_method_return(self):
        f_return = "SPAM eggs"
        self._method_delegator.trace_return(f_return)

        self.assertEqual(
            1, len(list_handler.records), repr(list_handler.records))

        return_record = list_handler.records[0]
        self.assertEqual(_class_logger.name, return_record.name)
        self.assertEqual("RETURN %r", return_record.msg)
        self.assertEqual((f_return,), return_record.args)
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertEqual(_expected_method_filename, return_record.pathname)
        self.assertEqual(_expected_method_lastlineno, return_record.lineno)
        self.assertEqual("method", return_record.funcName)


def suite():
    return unittest.makeSuite(TracingLoggerDelegatorTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

