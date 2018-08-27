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
:func:`autologging._FunctionTracingProxy`.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

from inspect import isgenerator
import logging
import unittest

from autologging import (
    TRACE,
    _FunctionTracingProxy,
    _GeneratorIteratorTracingProxy,
    __version__,
)

from test import get_lineno, has_co_lnotab, list_handler

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


def sample_function(arg, keyword=None): #s_f:L1
    x = arg.upper()
    return "%s %s" % (x, keyword) #s_f:LN


_expected_function_filename = sample_function.__code__.co_filename
_expected_function_firstlineno = get_lineno(
        _expected_function_filename, "#s_f:L1")
_expected_function_lastlineno = (get_lineno(
        _expected_function_filename, "#s_f:LN")
        if has_co_lnotab else _expected_function_firstlineno)


def sample_generator(count): #s_g:L1
    for i in range(count):
        yield i + 1 #s_g:LY


_expected_generator_filename = sample_generator.__code__.co_filename
_expected_generator_firstlineno = get_lineno(
        _expected_generator_filename, "#s_g:L1")
_expected_generator_lastlineno = (get_lineno(
        _expected_generator_filename, "#s_g:LY")
        if has_co_lnotab else _expected_generator_firstlineno)


class SampleClass(object):
    
    def method(self, arg, keyword=None): #SC.m:L1
        x = arg.upper()
        return "%s %s" % (x, keyword) #SC.m:LN


_method = SampleClass.__dict__["method"]
_expected_method_filename = _method.__code__.co_filename
_expected_method_firstlineno = get_lineno(
        _expected_method_filename, "#SC.m:L1")
_expected_method_lastlineno = (get_lineno(
        _expected_method_filename, "#SC.m:LN")
        if has_co_lnotab else _expected_method_firstlineno)

_module_logger = logging.getLogger(__name__)
_module_logger.setLevel(TRACE)
_module_logger.addHandler(list_handler)

_class_logger = logging.getLogger(__name__ + ".SampleClass")
_class_logger.propagate = False
_class_logger.setLevel(TRACE)
_class_logger.addHandler(list_handler)


class FunctionTracingProxyTest(unittest.TestCase):
    """Test the :class:`autologging._FunctionTracingProxy` class."""

    @classmethod
    def setUpClass(cls):
        cls._function_proxy = _FunctionTracingProxy(
                sample_function, _module_logger)
        cls._generator_proxy = _FunctionTracingProxy(
                sample_generator, _module_logger)
        cls._method_proxy = _FunctionTracingProxy(_method, _class_logger)

    def setUp(self):
        list_handler.reset()

    def test_init_sets_expected_log_record_attributes_for_function(self):
        self.assertEqual(
            _expected_function_filename,
            self._function_proxy._func_filename)
        self.assertEqual(
            _expected_function_firstlineno,
            self._function_proxy._func_firstlineno)
        self.assertEqual(
            _expected_function_lastlineno,
            self._function_proxy._func_lastlineno)

    def test_init_sets_expected_log_record_attributes_for_generator(self):
        self.assertEqual(
            _expected_generator_filename,
            self._generator_proxy._func_filename)
        self.assertEqual(
            _expected_generator_firstlineno,
            self._generator_proxy._func_firstlineno)
        self.assertEqual(
            _expected_generator_lastlineno,
            self._generator_proxy._func_lastlineno)

    def test_init_sets_expected_log_record_attributes_for_method(self):
        self.assertEqual(
            _expected_method_filename, self._method_proxy._func_filename)
        self.assertEqual(
            _expected_method_firstlineno,
            self._method_proxy._func_firstlineno)
        self.assertEqual(
            _expected_method_lastlineno, self._method_proxy._func_lastlineno)

    def test_trace_function_call(self):
        f_args = ("spam",)
        f_keywords = dict(keyword="eggs")
        self._function_proxy(sample_function, f_args, f_keywords)

        self.assertEqual(2, len(list_handler.records))

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
        f_args = ("spam",)
        f_keywords = dict(keyword="eggs")
        f_return = "SPAM eggs"
        rv = self._function_proxy(sample_function, f_args, f_keywords)

        self.assertEqual(f_return, rv)
        self.assertEqual(2, len(list_handler.records))

        return_record = list_handler.records[1]
        self.assertEqual(_module_logger.name, return_record.name)
        self.assertEqual("RETURN %r", return_record.msg)
        self.assertEqual((f_return,), return_record.args)
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertEqual(_expected_function_filename, return_record.pathname)
        self.assertEqual(_expected_function_lastlineno, return_record.lineno)
        self.assertEqual("sample_function", return_record.funcName)

    def test_trace_generator_call(self):
        f_args = (3,)
        f_keywords = {}
        self._generator_proxy(sample_generator, f_args, f_keywords)

        self.assertEqual(2, len(list_handler.records))

        call_record = list_handler.records[0]
        self.assertEqual(_module_logger.name, call_record.name)
        self.assertEqual("CALL *%r **%r", call_record.msg)
        self.assertEqual((f_args, {}), call_record.args)
        self.assertEqual("TRACE", call_record.levelname)
        self.assertEqual(TRACE, call_record.levelno)
        self.assertEqual(_expected_generator_filename, call_record.pathname)
        self.assertEqual(_expected_generator_firstlineno, call_record.lineno)
        self.assertEqual("sample_generator", call_record.funcName)

    def test_trace_generator_return(self):
        f_args = (3,)
        f_keywords = {}
        rv = self._generator_proxy(sample_generator, f_args, f_keywords)

        # unexpected closure behavior:
        # the _GeneratorIteratorTracingProxy class object that is the result
        # of type(rv) is NOT the same object as the one that is imported from
        # the module!
        #self.assertTrue(type(rv) is _GeneratorIteratorTracingProxy)
        self.assertTrue(type(rv).__name__ == "_GeneratorIteratorTracingProxy")
        self.assertEqual(2, len(list_handler.records))

        return_record = list_handler.records[1]
        self.assertEqual(_module_logger.name, return_record.name)
        self.assertEqual("RETURN %r", return_record.msg)
        self.assertEqual(1, len(return_record.args))
        self.assertTrue(return_record.args[0] is rv.__wrapped__)
        self.assertTrue(isgenerator(return_record.args[0]))
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertEqual(_expected_generator_filename, return_record.pathname)
        self.assertEqual(_expected_generator_lastlineno, return_record.lineno)
        self.assertEqual("sample_generator", return_record.funcName)

    def test_trace_method_call(self):
        f_args = ("spam",)
        f_keywords = dict(keyword="eggs")
        obj = SampleClass()
        method = _method.__get__(obj, SampleClass)
        self._method_proxy(method, f_args, f_keywords)

        self.assertEqual(2, len(list_handler.records))

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
        f_args = ("spam",)
        f_keywords = dict(keyword="eggs")
        f_return = "SPAM eggs"
        obj = SampleClass()
        method = _method.__get__(obj, SampleClass)
        rv = self._method_proxy(method, f_args, f_keywords)

        self.assertEqual(f_return, rv)
        self.assertEqual(2, len(list_handler.records))

        return_record = list_handler.records[1]
        self.assertEqual(_class_logger.name, return_record.name)
        self.assertEqual("RETURN %r", return_record.msg)
        self.assertEqual((f_return,), return_record.args)
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertEqual(_expected_method_filename, return_record.pathname)
        self.assertEqual(_expected_method_lastlineno, return_record.lineno)
        self.assertEqual("method", return_record.funcName)


def suite():
    return unittest.makeSuite(FunctionTracingProxyTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

