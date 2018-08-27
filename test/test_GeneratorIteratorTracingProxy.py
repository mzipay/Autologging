# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2015, 2016, 2018 Matthew Zipay.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""Test case and runner for
:func:`autologging._GeneratorIteratorTracingProxy`.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

from inspect import isgenerator
import logging
import unittest

from autologging import (
    _is_ironpython,
    TRACE,
    _GeneratorIteratorTracingProxy,
    __version__,
)

from test import get_lineno, has_co_lnotab, list_handler

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


def sample_generator(count): #s_g:L1
    for i in range(count):
        yield i + 1 #s_g:LY


_expected_function_filename = sample_generator.__code__.co_filename
# generator iterators have a built-in reference to a frame object, so the
# line number *should* be consistent... except for IronPython
_expected_function_lineno = (
        get_lineno(_expected_function_filename, "#s_g:LY")
        if not _is_ironpython else
        get_lineno(_expected_function_filename, "#s_g:L1"))


class SampleClass(object):
    
    def method(self, count): #SC.m:L1
        for i in range(count):
            yield i + 1 #SC.m:LY


_method = SampleClass.__dict__["method"]
_expected_method_filename = _method.__code__.co_filename
# generator iterators have a built-in reference to a frame object, so the
# line number *should* be consistent... except for IronPython
_expected_method_lineno = (
        get_lineno(_expected_function_filename, "#SC.m:LY")
        if not _is_ironpython else
        get_lineno(_expected_function_filename, "#SC.m:L1"))

_module_logger = logging.getLogger(__name__)
_module_logger.setLevel(TRACE)
_module_logger.addHandler(list_handler)

_class_logger = logging.getLogger(__name__ + ".SampleClass")
_class_logger.propagate = False
_class_logger.setLevel(TRACE)
_class_logger.addHandler(list_handler)


class GeneratorIteratorTracingProxyTest(unittest.TestCase):
    """Test the
    :class:`autologging._GeneratorIteratorTracingProxy` class.

    """

    @classmethod
    def setUpClass(cls):
        # note: generator iterators cannot be "rewound"
        cls._function_proxy = _GeneratorIteratorTracingProxy(
                sample_generator, sample_generator(2), _module_logger)
        cls._method_proxy = _GeneratorIteratorTracingProxy(
                SampleClass.__dict__["method"], SampleClass().method(2),
                _class_logger)

    def setUp(self):
        list_handler.reset()

    def test_trace_function_yield_stop(self):
        self.assertEqual([1, 2], list(self._function_proxy))
        self.assertEqual(3, len(list_handler.records))

        yield1_record = list_handler.records[0]
        self.assertEqual(_module_logger.name, yield1_record.name)
        self.assertEqual("YIELD %r", yield1_record.msg)
        self.assertEqual((1,), yield1_record.args)
        self.assertEqual("TRACE", yield1_record.levelname)
        self.assertEqual(TRACE, yield1_record.levelno)
        self.assertEqual(_expected_function_filename, yield1_record.pathname)
        self.assertEqual(_expected_function_lineno, yield1_record.lineno)
        self.assertEqual("sample_generator", yield1_record.funcName)

        yield2_record = list_handler.records[1]
        self.assertEqual(_module_logger.name, yield2_record.name)
        self.assertEqual("YIELD %r", yield2_record.msg)
        self.assertEqual((2,), yield2_record.args)
        self.assertEqual("TRACE", yield2_record.levelname)
        self.assertEqual(TRACE, yield2_record.levelno)
        self.assertEqual(_expected_function_filename, yield2_record.pathname)
        self.assertEqual(_expected_function_lineno, yield2_record.lineno)
        self.assertEqual("sample_generator", yield2_record.funcName)

        stop_record = list_handler.records[2]
        self.assertEqual(_module_logger.name, stop_record.name)
        self.assertEqual("STOP", stop_record.msg)
        self.assertEqual(tuple(), stop_record.args)
        self.assertEqual("TRACE", stop_record.levelname)
        self.assertEqual(TRACE, stop_record.levelno)
        self.assertEqual(_expected_function_filename, stop_record.pathname)
        self.assertEqual(_expected_function_lineno, stop_record.lineno)
        self.assertEqual("sample_generator", stop_record.funcName)

    def test_trace_method_yield_stop(self):
        self.assertEqual([1, 2], list(self._method_proxy))
        self.assertEqual(3, len(list_handler.records))

        yield1_record = list_handler.records[0]
        self.assertEqual(_class_logger.name, yield1_record.name)
        self.assertEqual("YIELD %r", yield1_record.msg)
        self.assertEqual((1,), yield1_record.args)
        self.assertEqual("TRACE", yield1_record.levelname)
        self.assertEqual(TRACE, yield1_record.levelno)
        self.assertEqual(_expected_method_filename, yield1_record.pathname)
        self.assertEqual(_expected_method_lineno, yield1_record.lineno)
        self.assertEqual("method", yield1_record.funcName)

        yield2_record = list_handler.records[1]
        self.assertEqual(_class_logger.name, yield2_record.name)
        self.assertEqual("YIELD %r", yield2_record.msg)
        self.assertEqual((2,), yield2_record.args)
        self.assertEqual("TRACE", yield2_record.levelname)
        self.assertEqual(TRACE, yield2_record.levelno)
        self.assertEqual(_expected_method_filename, yield2_record.pathname)
        self.assertEqual(_expected_method_lineno, yield2_record.lineno)
        self.assertEqual("method", yield2_record.funcName)

        stop_record = list_handler.records[2]
        self.assertEqual(_class_logger.name, stop_record.name)
        self.assertEqual("STOP", stop_record.msg)
        self.assertEqual(tuple(), stop_record.args)
        self.assertEqual("TRACE", stop_record.levelname)
        self.assertEqual(TRACE, stop_record.levelno)
        self.assertEqual(_expected_method_filename, stop_record.pathname)
        self.assertEqual(_expected_method_lineno, stop_record.lineno)
        self.assertEqual("method", stop_record.funcName)


def suite():
    return unittest.makeSuite(GeneratorIteratorTracingProxyTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

