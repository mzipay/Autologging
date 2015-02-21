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

"""Test cases and runner for various non-public/internal functions and
classes of the :mod:`autologging` module.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.4.0"

import logging
import unittest
import warnings

from autologging import (
    _add_logger_to,
    _get_default_traceable_method_names,
    _get_traceable_method_names,
    _make_function_tracer,
    _make_instancemethod_tracer,
    _make_classmethod_tracer,
    _make_staticmethod_tracer,
    _mangle,
    _is_private,
    _is_special,
    TRACE,
    _TracingLoggerDelegator,
)

from test import (
    dummy_module_logger,
    get_dummy_lineno,
    list_handler,
    named_tracer,
)
from test.dummy import (
    dummyM_module_logger,
    get_dummyM_lineno,
    logged_and_traced_function,
    LoggedAndTracedClass,
)

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)

_public_names = ["public", "public_name", "public_", "public__", "Public"]
_nonpublic_names = ["_nonpublic", "_non_public", "_nonpublic_", "_nonpublic__",
                    "_NonPublic"]
_private_names = ["__private", "__private_name", "__private_", "__Private"]
_special_names = ["__special__", "__special_name__"]


class IsPrivateTest(unittest.TestCase):

    def test_public_name(self):
        for name in _public_names:
            self.assertFalse(_is_private(name), name)

    def test_nonpublic_name(self):
        for name in _nonpublic_names:
            self.assertFalse(_is_private(name), name)

    def test_special_name(self):
        for name in _special_names:
            self.assertFalse(_is_private(name), name)

    def test_private_name(self):
        for name in _private_names:
            self.assertTrue(_is_private(name), name)


class IsSpecialTest(unittest.TestCase):

    def test_public_name(self):
        for name in _public_names:
            self.assertFalse(_is_special(name), name)

    def test_nonpublic_name(self):
        for name in _nonpublic_names:
            self.assertFalse(_is_special(name), name)

    def test_special_name(self):
        for name in _special_names:
            self.assertTrue(_is_special(name), name)

    def test_private_name(self):
        for name in _private_names:
            self.assertFalse(_is_special(name), name)


class MangleTest(unittest.TestCase):

    def test_mangle_with_public_class_name(self):
        for name in _private_names:
            self.assertEqual("_ClassName" + name, _mangle(name, "ClassName"))

    def test_mangle_with_nonpublic_class_name(self):
        for name in _private_names:
            self.assertEqual("_ClassName" + name, _mangle(name, "_ClassName"))

    def test_mangle_with_private_class_name(self):
        for name in _private_names:
            self.assertEqual("_ClassName" + name, _mangle(name, "__ClassName"))


def _sample_function(arg, keyword=None):
    return "%s and %s" % (arg, keyword)


class _SampleClass(object):

    ATTRIBUTE = None

    @staticmethod
    def static_method(arg, keyword=None):
        return "%s and %s" % (arg, keyword)

    @classmethod
    def class_method(cls, arg, keyword=None):
        return "%s and %s" % (arg, keyword)

    def __init__(self): pass

    def public(self, arg, keyword=None):
        return "%s and %s" % (arg, keyword)

    def _nonpublic(self): pass

    def __private(self): pass

    def __special__(self): pass


class AddLoggerToTest(unittest.TestCase):

    def tearDown(self):
        if (hasattr(_SampleClass, "_SampleClass__logger")):
            delattr(_SampleClass, "_SampleClass__logger")
        if (hasattr(_sample_function, "_logger")):
            delattr(_sample_function, "_logger")

    def test_add_logger_to_class(self):
        self.assertFalse(hasattr(_SampleClass, "_SampleClass__logger"))
        _add_logger_to(_SampleClass, "parent")
        self.assertIsNotNone(_SampleClass._SampleClass__logger)
        self.assertEqual("parent._SampleClass",
                         _SampleClass._SampleClass__logger.name)

    def test_add_logger_to_function(self):
        self.assertFalse(hasattr(_sample_function, "_logger"))
        _add_logger_to(_sample_function, "parent")
        self.assertIsNotNone(_sample_function._logger)
        self.assertEqual("parent", _sample_function._logger.name)


class GetDefaultTraceableMethodNamesTest(unittest.TestCase):

    def test_do_not_include_special_methods(self):
        expected_method_names = [
            "static_method",
            "class_method",
            "__init__",
            "public",
            "_nonpublic",
            "_SampleClass__private",
        ]
        actual_method_names = \
            _get_default_traceable_method_names(_SampleClass.__dict__)
        self.assertEqual(sorted(expected_method_names), 
                         sorted(actual_method_names))

    def test_include_special_methods(self):
        expected_method_names = [
            "static_method",
            "class_method",
            "__init__",
            "public",
            "_nonpublic",
            "_SampleClass__private",
            "__special__",
        ]
        actual_method_names = \
            _get_default_traceable_method_names(_SampleClass.__dict__,
                                                include_special_methods=True)
        self.assertEqual(sorted(expected_method_names), 
                         sorted(actual_method_names))


class GetTraceableMethodNamesTest(unittest.TestCase):

    def test_valid_method_names(self):
        expected_method_names = ["public", "_nonpublic", "_SampleClass__private"]
        actual_method_names = _get_traceable_method_names(
            ["public", "_nonpublic", "__private"],
            "_SampleClass", _SampleClass.__dict__)
        self.assertEqual(sorted(expected_method_names), 
                         sorted(actual_method_names))

    def test_invalid_method_names(self):
        expected_method_names = ["public", "_nonpublic", "_SampleClass__private"]
        with warnings.catch_warnings(record=True) as caught_warnings:
            actual_method_names = _get_traceable_method_names(
                ["ATTRIBUTE", "public", "_nonpublic", "__private", "nonexistent"],
                "_SampleClass", _SampleClass.__dict__)
            self.assertEqual(2, len(caught_warnings))
            self.assertIsInstance(caught_warnings[-2].message, UserWarning)
            self.assertEqual(
                "'ATTRIBUTE' does not identify a method defined in _SampleClass",
                caught_warnings[-2].message.args[0])
            self.assertIsInstance(caught_warnings[-1].message, UserWarning)
            self.assertEqual(
                "'nonexistent' does not identify a method defined in _SampleClass",
                caught_warnings[-1].message.args[0])
            self.assertEqual(sorted(expected_method_names), 
                             sorted(actual_method_names))


class TracingLoggerDelegatorTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._parent_logger = logging.getLogger("parent")
        cls._parent_logger.addHandler(list_handler)

        cls._child_logger = logging.getLogger("parent.child")
        cls._child_logger.addHandler(list_handler)

    def setUp(self):
        list_handler.reset()
        self._parent_logger.setLevel(logging.NOTSET)
        self._child_logger.setLevel(logging.NOTSET)

    def tearDown(self):
        list_handler.setLevel(TRACE)

    def test_find_last_line_number(self):
        self.assertEqual(_sample_function.__code__.co_firstlineno + 1,
                         _TracingLoggerDelegator._find_last_line_number(
                            _sample_function.__code__))

    def test_delegation(self):
        self._parent_logger.setLevel(logging.INFO)

        logger_delegator = _TracingLoggerDelegator(self._child_logger,
                                                   _sample_function)

        self.assertEqual("parent.child", logger_delegator.name)
        self.assertEqual(logging.NOTSET, logger_delegator.level)
        self.assertTrue(logger_delegator.parent is self._parent_logger)
        self.assertEqual(logging.INFO, logger_delegator.getEffectiveLevel())
        self.assertFalse(logger_delegator.isEnabledFor(logging.DEBUG))
        self.assertTrue(logger_delegator.isEnabledFor(logging.INFO))

    def test_caller_info(self):
        logger_delegator = _TracingLoggerDelegator(self._child_logger,
                                                   _sample_function)

        self.assertEqual("_sample_function", logger_delegator._caller_name)
        self.assertTrue(
            logger_delegator._caller_filename.endswith(
                "test/test_autologging.py"))
        self.assertEqual(_sample_function.__code__.co_firstlineno,
                         logger_delegator._caller_firstlineno)
        self.assertEqual(_sample_function.__code__.co_firstlineno + 1,
                         logger_delegator._caller_lastlineno)

    def test_log_call_trace_disabled(self):
        # log_call bypasses the logger level checks (those checks are handled
        # by the tracing proxy funtions) because the logger delegator must
        # create the logging.LogRecord objects itself in order to inject the
        # correct caller information; therefore, in order to disable tracing
        # in this test we need to set the *handler* threshold to something
        # higher than TRACE
        list_handler.setLevel(logging.DEBUG)
        logger_delegator = _TracingLoggerDelegator(self._child_logger,
                                                   _sample_function)
        logger_delegator.log_call(tuple(), dict())

        self.assertEqual(0, len(list_handler.records))

    def test_log_call_trace_enabled(self):
        # list_handler is shared, so make sure records do not propagate
        self._child_logger.propagate = False
        logger_delegator = _TracingLoggerDelegator(self._child_logger,
                                                   _sample_function)
        logger_delegator.log_call(("spam",), {"keyword": "eggs"})

        self.assertEqual(1, len(list_handler.records))

        record = list_handler.records.pop()
        self.assertEqual("parent.child", record.name)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(logger_delegator._caller_filename, record.pathname)
        self.assertEqual(logger_delegator._caller_firstlineno, record.lineno)
        self.assertEqual("_sample_function", record.funcName)
        self.assertEqual("CALL *%r **%r", record.msg)
        self.assertEqual((("spam",), {"keyword": "eggs"}), record.args)
        self.assertEqual("CALL *('spam',) **{'keyword': 'eggs'}",
                         record.getMessage())

    def test_log_return_trace_disabled(self):
        # log_return bypasses the logger level checks (those checks are handled
        # by the tracing proxy funtions) because the logger delegator must
        # create the logging.LogRecord objects itself in order to inject the
        # correct caller information; therefore, in order to disable tracing
        # in this test we need to set the *handler* threshold to something
        # higher than TRACE
        list_handler.setLevel(logging.DEBUG)
        logger_delegator = _TracingLoggerDelegator(self._child_logger,
                                                   _sample_function)
        logger_delegator.log_return("spam and eggs")

        self.assertEqual(0, len(list_handler.records))

    def test_log_return_trace_enabled(self):
        # list_handler is shared, so make sure records do not propagate
        self._child_logger.propagate = False
        logger_delegator = _TracingLoggerDelegator(self._child_logger,
                                                   _sample_function)
        logger_delegator.log_return("spam and eggs")

        self.assertEqual(1, len(list_handler.records))

        record = list_handler.records.pop()
        self.assertEqual("parent.child", record.name)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(logger_delegator._caller_filename, record.pathname)
        self.assertEqual(logger_delegator._caller_lastlineno, record.lineno)
        self.assertEqual("_sample_function", record.funcName)
        self.assertEqual("RETURN %r", record.msg)
        self.assertEqual(("spam and eggs",), record.args)
        self.assertEqual("RETURN 'spam and eggs'", record.getMessage())


class _MakeTracerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._logger = logging.getLogger("parent.child")
        cls._logger.addHandler(list_handler)

    def setUp(self):
        list_handler.reset()
        self._logger.setLevel(logging.NOTSET)

    def _assert_trace_log_records(self, proxy_function, lastlineno_offset=1):
        return_record = list_handler.records.pop()
        self.assertEqual("parent.child", return_record.name)
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertEqual(proxy_function.__wrapped__.__code__.co_filename,
                         return_record.pathname)
        self.assertEqual(proxy_function.__wrapped__.__code__.co_firstlineno +
                            lastlineno_offset,
                         return_record.lineno)
        self.assertEqual(proxy_function.__wrapped__.__name__,
                         return_record.funcName)
        self.assertEqual("RETURN %r", return_record.msg)
        self.assertEqual(("spam and eggs",), return_record.args)
        self.assertEqual("RETURN 'spam and eggs'", return_record.getMessage())

        call_record = list_handler.records.pop()
        self.assertEqual("parent.child", call_record.name)
        self.assertEqual("TRACE", call_record.levelname)
        self.assertEqual(TRACE, call_record.levelno)
        self.assertEqual(proxy_function.__wrapped__.__code__.co_filename,
                         call_record.pathname)
        self.assertEqual(proxy_function.__wrapped__.__code__.co_firstlineno,
                         call_record.lineno)
        self.assertEqual(proxy_function.__wrapped__.__name__,
                         call_record.funcName)
        self.assertEqual("CALL *%r **%r", call_record.msg)
        self.assertEqual((("spam",), {"keyword": "eggs"}), call_record.args)
        self.assertEqual("CALL *('spam',) **{'keyword': 'eggs'}",
                         call_record.getMessage())


class MakeFunctionTracerTest(_MakeTracerTest):

    def test_create_proxy_function(self):
        self._logger.setLevel(TRACE)
        proxy_function = _make_function_tracer(_sample_function, self._logger)

        self.assertTrue(proxy_function.__wrapped__ is _sample_function)

        var_index = \
            proxy_function.__code__.co_freevars.index("logger_delegator")
        logger_delegator = proxy_function.__closure__[var_index].cell_contents
        self.assertEqual("parent.child", logger_delegator.name)
        self.assertEqual(TRACE, logger_delegator.level)

    def test_proxy_trace_disabled(self):
        self._logger.setLevel(logging.DEBUG)
        proxy_function = _make_function_tracer(_sample_function, self._logger)

        self.assertTrue(proxy_function.__wrapped__ is _sample_function)

        proxy_function("spam", keyword="eggs")
        self.assertEqual(0, len(list_handler.records))

    def test_proxy_trace_enabled(self):
        self._logger.setLevel(TRACE)
        proxy_function = _make_function_tracer(_sample_function, self._logger)

        self.assertTrue(proxy_function.__wrapped__ is _sample_function)

        proxy_function("spam", keyword="eggs")
        self.assertEqual(2, len(list_handler.records))
        self._assert_trace_log_records(proxy_function)


class MakeStaticMethodTracerTest(_MakeTracerTest):

    def test_create_proxy_function(self):
        self._logger.setLevel(TRACE)
        descriptor = _make_staticmethod_tracer(
            _SampleClass.__dict__["static_method"], self._logger)
        proxy_function = descriptor.__get__(None, _SampleClass)

        self.assertTrue(proxy_function.__wrapped__ is
                        _SampleClass.__dict__["static_method"].__func__)

        var_index = \
            proxy_function.__code__.co_freevars.index("logger_delegator")
        logger_delegator = proxy_function.__closure__[var_index].cell_contents
        self.assertEqual("parent.child", logger_delegator.name)
        self.assertEqual(TRACE, logger_delegator.level)

    def test_proxy_trace_disabled(self):
        self._logger.setLevel(logging.DEBUG)
        descriptor = _make_staticmethod_tracer(
            _SampleClass.__dict__["static_method"], self._logger)
        proxy_function = descriptor.__get__(None, _SampleClass)

        self.assertTrue(proxy_function.__wrapped__ is
                        _SampleClass.__dict__["static_method"].__func__)

        proxy_function("spam", keyword="eggs")
        self.assertEqual(0, len(list_handler.records))

    def test_proxy_trace_enabled(self):
        self._logger.setLevel(TRACE)
        descriptor = _make_staticmethod_tracer(
            _SampleClass.__dict__["static_method"], self._logger)
        proxy_function = descriptor.__get__(None, _SampleClass)

        self.assertTrue(proxy_function.__wrapped__ is
                        _SampleClass.__dict__["static_method"].__func__)

        proxy_function("spam", keyword="eggs")
        self.assertEqual(2, len(list_handler.records))
        self._assert_trace_log_records(proxy_function, lastlineno_offset=2)


class MakeClassMethodTracerTest(_MakeTracerTest):

    def test_create_proxy_function(self):
        self._logger.setLevel(TRACE)
        descriptor = _make_classmethod_tracer(
            _SampleClass.__dict__["class_method"], self._logger)
        proxy_function = descriptor.__get__(None, _SampleClass)

        self.assertTrue(proxy_function.__wrapped__ is
                        _SampleClass.__dict__["class_method"].__func__)

        var_index = \
            proxy_function.__code__.co_freevars.index("logger_delegator")
        logger_delegator = proxy_function.__closure__[var_index].cell_contents
        self.assertEqual("parent.child", logger_delegator.name)
        self.assertEqual(TRACE, logger_delegator.level)

    def test_proxy_trace_disabled(self):
        self._logger.setLevel(logging.DEBUG)
        descriptor = _make_classmethod_tracer(
            _SampleClass.__dict__["class_method"], self._logger)
        proxy_function = descriptor.__get__(None, _SampleClass)

        self.assertTrue(proxy_function.__wrapped__ is
                        _SampleClass.__dict__["class_method"].__func__)

        proxy_function("spam", keyword="eggs")
        self.assertEqual(0, len(list_handler.records))

    def test_proxy_trace_enabled(self):
        self._logger.setLevel(TRACE)
        descriptor = _make_classmethod_tracer(
            _SampleClass.__dict__["class_method"], self._logger)
        proxy_function = descriptor.__get__(None, _SampleClass)

        self.assertTrue(proxy_function.__wrapped__ is
                        _SampleClass.__dict__["class_method"].__func__)

        proxy_function("spam", keyword="eggs")
        self.assertEqual(2, len(list_handler.records))
        self._assert_trace_log_records(proxy_function, lastlineno_offset=2)


class MakeInstanceMethodTracerTest(_MakeTracerTest):

    def test_create_proxy_function(self):
        self._logger.setLevel(TRACE)
        descriptor = _make_instancemethod_tracer(
            _SampleClass.__dict__["public"], self._logger)
        proxy_function = descriptor.__get__(_SampleClass())

        self.assertTrue(proxy_function.__wrapped__ is
                        _SampleClass.__dict__["public"])

        var_index = \
            proxy_function.__code__.co_freevars.index("logger_delegator")
        logger_delegator = proxy_function.__closure__[var_index].cell_contents
        self.assertEqual("parent.child", logger_delegator.name)
        self.assertEqual(TRACE, logger_delegator.level)

    def test_proxy_trace_disabled(self):
        self._logger.setLevel(logging.DEBUG)
        descriptor = _make_instancemethod_tracer(
            _SampleClass.__dict__["public"], self._logger)
        proxy_function = descriptor.__get__(_SampleClass())

        self.assertTrue(proxy_function.__wrapped__ is
                        _SampleClass.__dict__["public"])

        proxy_function("spam", keyword="eggs")
        self.assertEqual(0, len(list_handler.records))

    def test_proxy_trace_enabled(self):
        self._logger.setLevel(TRACE)
        descriptor = _make_instancemethod_tracer(
            _SampleClass.__dict__["public"], self._logger)
        proxy_function = descriptor.__get__(_SampleClass())

        self.assertTrue(proxy_function.__wrapped__ is
                        _SampleClass.__dict__["public"])

        proxy_function("spam", keyword="eggs")
        self.assertEqual(2, len(list_handler.records))
        self._assert_trace_log_records(proxy_function)


class LoggedAndTracedFunctionTest(unittest.TestCase):

    @classmethod
    def tearDownClass(self):
        dummy_module_logger.setLevel(logging.NOTSET)
        named_tracer.setLevel(TRACE)
        list_handler.setLevel(TRACE)

    def setUp(self):
        list_handler.reset()

    def tearDown(self):
        dummy_module_logger.setLevel(logging.NOTSET)
        named_tracer.setLevel(TRACE)
        list_handler.setLevel(TRACE)

    def test_log_disabled_trace_disabled(self):
        dummy_module_logger.setLevel(logging.WARNING)
        named_tracer.setLevel(logging.NOTSET)
        logged_and_traced_function()

        self.assertEqual(0, len(list_handler.records))

    def test_log_enabled_trace_disabled(self):
        dummy_module_logger.setLevel(logging.INFO)
        named_tracer.setLevel(logging.NOTSET)
        logged_and_traced_function()

        self.assertEqual(1, len(list_handler.records))
        self._assert_log_record()

    def _assert_log_record(self):
        record = list_handler.records.pop()
        self.assertEqual("test.dummy", record.name)
        self.assertEqual("logged_and_traced_function", record.funcName)

    def test_log_disabled_trace_enabled(self):
        dummy_module_logger.setLevel(logging.WARNING)
        named_tracer.setLevel(TRACE)
        logged_and_traced_function()

        self.assertEqual(2, len(list_handler.records))
        self._assert_trace_return_record()
        self._assert_trace_call_record()

    def _assert_trace_return_record(self):
        return_record = list_handler.records.pop()
        self.assertEqual("traced.testing", return_record.name)
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertEqual(
            logged_and_traced_function.__wrapped__.__code__.co_filename,
            return_record.pathname)
        self.assertEqual(get_dummy_lineno("#l_a_t_f:LN"),
                         return_record.lineno)
        self.assertEqual("logged_and_traced_function", return_record.funcName)
        self.assertEqual("RETURN %r", return_record.msg)
        self.assertEqual((None,), return_record.args)

    def _assert_trace_call_record(self):
        call_record = list_handler.records.pop()
        self.assertEqual("traced.testing", call_record.name)
        self.assertEqual("TRACE", call_record.levelname)
        self.assertEqual(TRACE, call_record.levelno)
        self.assertEqual(
            logged_and_traced_function.__wrapped__.__code__.co_filename,
            call_record.pathname)
        self.assertEqual(get_dummy_lineno("#l_a_t_f:L1"),
                         call_record.lineno)
        self.assertEqual("logged_and_traced_function", call_record.funcName)
        self.assertEqual("CALL *%r **%r", call_record.msg)
        self.assertEqual((tuple(), dict()), call_record.args)

    def test_log_enabled_trace_enabled(self):
        dummy_module_logger.setLevel(logging.INFO)
        named_tracer.setLevel(TRACE)
        logged_and_traced_function()

        self.assertEqual(3, len(list_handler.records))
        self._assert_trace_return_record()
        self._assert_log_record()
        self._assert_trace_call_record()


class LoggedAndTracedClassTest(unittest.TestCase):

    @classmethod
    def tearDownClass(self):
        dummyM_module_logger.setLevel(logging.NOTSET)
        named_tracer.setLevel(TRACE)
        list_handler.setLevel(TRACE)

    def setUp(self):
        list_handler.reset()
        self._obj = LoggedAndTracedClass()

    def tearDown(self):
        dummyM_module_logger.setLevel(logging.NOTSET)
        named_tracer.setLevel(TRACE)
        list_handler.setLevel(TRACE)
        self._obj = None

    def test_log_disabled_trace_disabled(self):
        dummyM_module_logger.setLevel(logging.WARNING)
        named_tracer.setLevel(logging.NOTSET)
        self._obj.method()

        self.assertEqual(0, len(list_handler.records))

    def test_log_enabled_trace_disabled(self):
        dummyM_module_logger.setLevel(logging.INFO)
        named_tracer.setLevel(logging.NOTSET)
        self._obj.method()

        self.assertEqual(1, len(list_handler.records))
        self._assert_log_record()

    def _assert_log_record(self):
        record = list_handler.records.pop()
        self.assertEqual("%s.LoggedAndTracedClass" % dummyM_module_logger.name,
                         record.name)
        self.assertEqual("method", record.funcName)

    def test_log_disabled_trace_enabled(self):
        dummyM_module_logger.setLevel(logging.WARNING)
        named_tracer.setLevel(TRACE)
        self._obj.method()

        self.assertEqual(2, len(list_handler.records))
        self._assert_trace_return_record()
        self._assert_trace_call_record()

    def _assert_trace_return_record(self):
        return_record = list_handler.records.pop()
        self.assertEqual("traced.testing.LoggedAndTracedClass",
                         return_record.name)
        self.assertEqual("TRACE", return_record.levelname)
        self.assertEqual(TRACE, return_record.levelno)
        self.assertEqual(self._obj.method.__wrapped__.__code__.co_filename,
                         return_record.pathname)
        self.assertEqual(get_dummyM_lineno("#LATC.m:LN"),
                         return_record.lineno)
        self.assertEqual("method", return_record.funcName)
        self.assertEqual("RETURN %r", return_record.msg)
        self.assertEqual((None,), return_record.args)

    def _assert_trace_call_record(self):
        call_record = list_handler.records.pop()
        self.assertEqual("traced.testing.LoggedAndTracedClass",
                         call_record.name)
        self.assertEqual("TRACE", call_record.levelname)
        self.assertEqual(TRACE, call_record.levelno)
        self.assertEqual(self._obj.method.__wrapped__.__code__.co_filename,
                         call_record.pathname)
        self.assertEqual(get_dummyM_lineno("#LATC.m:L1"),
                         call_record.lineno)
        self.assertEqual("method", call_record.funcName)
        self.assertEqual("CALL *%r **%r", call_record.msg)
        self.assertEqual((tuple(), dict()), call_record.args)

    def test_log_enabled_trace_enabled(self):
        dummyM_module_logger.setLevel(logging.INFO)
        named_tracer.setLevel(TRACE)
        self._obj.method()

        self.assertEqual(3, len(list_handler.records))
        self._assert_trace_return_record()
        self._assert_log_record()
        self._assert_trace_call_record()


def suite():
    """Build the test suite for :func:`autologging.logged`."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IsPrivateTest))
    suite.addTest(unittest.makeSuite(IsSpecialTest))
    suite.addTest(unittest.makeSuite(MangleTest))
    suite.addTest(unittest.makeSuite(AddLoggerToTest))
    suite.addTest(unittest.makeSuite(GetDefaultTraceableMethodNamesTest))
    suite.addTest(unittest.makeSuite(GetTraceableMethodNamesTest))
    suite.addTest(unittest.makeSuite(TracingLoggerDelegatorTest))
    suite.addTest(unittest.makeSuite(MakeFunctionTracerTest))
    suite.addTest(unittest.makeSuite(MakeStaticMethodTracerTest))
    suite.addTest(unittest.makeSuite(MakeClassMethodTracerTest))
    suite.addTest(unittest.makeSuite(MakeInstanceMethodTracerTest))
    suite.addTest(unittest.makeSuite(LoggedAndTracedFunctionTest))
    suite.addTest(unittest.makeSuite(LoggedAndTracedClassTest))

    return suite


if (__name__ == "__main__"):
    unittest.TextTestRunner().run(suite())

