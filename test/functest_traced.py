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

"""Functional test cases and runner for the :func:`autologging.traced`
decorator function.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import TRACE, __version__, _is_ironpython

from test import (
    dummy_module_logger,
    get_dummy_lineno,
    has_co_lnotab,
    list_handler,
    named_tracer,
)
from test.dummy import TracedClass, traced_function

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class _TracedFunctionalTest(unittest.TestCase):

    def setUp(self):
        dummy_module_logger.setLevel(TRACE)
        named_tracer.setLevel(TRACE)
        list_handler.reset()

    def _assert_call_record(
            self, call_record, traced_function, expected_logger_name,
            expected_args, marker):
        self._assert_trace_record(
            call_record, traced_function, expected_logger_name,
            "CALL *%r **%r", expected_args,
            get_dummy_lineno("#%s:L1" % marker))

    def _assert_return_record(
            self, return_record, traced_function, expected_logger_name,
            expected_args, marker):
        self._assert_trace_record(
            return_record, traced_function, expected_logger_name, "RETURN %r",
            expected_args,
            get_dummy_lineno(
                ("#%s:LN" if has_co_lnotab else "#%s:L1") % marker))

    def _assert_trace_record(
            self, trace_record, traced_function, expected_logger_name,
            expected_msg, expected_args, expected_lineno):
        self.assertEqual(expected_logger_name, trace_record.name)
        self.assertEqual(expected_msg, trace_record.msg)
        self.assertEqual(expected_args, trace_record.args)
        self.assertEqual("TRACE", trace_record.levelname)
        self.assertEqual(TRACE, trace_record.levelno)
        # IronPython doesn't handle frames or code objects fully (even with
        # -X:FullFrames)
        if not _is_ironpython:
            self.assertEqual(
                traced_function.__code__.co_filename, trace_record.pathname)
            self.assertEqual(expected_lineno, trace_record.lineno)
            self.assertEqual(traced_function.__name__, trace_record.funcName)


class TracedClassFunctionalTest(_TracedFunctionalTest):
    """Test the trace records emitted by an :func:`autologging.traced`
    decorated class.

    """

    def test_staticmethod_tracing_log_records(self):
        value = TracedClass.static_method(None)

        self.assertEqual("TC.s_m None and None", value)
        self.assertEqual(2, len(list_handler.records))

        traced_function = \
            TracedClass.__dict__["static_method"].__func__.__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function, "test.dummy.TracedClass",
            ((None,), dict()), "TC.s_m")
        self._assert_return_record(
            list_handler.records[1], traced_function, "test.dummy.TracedClass",
            ("TC.s_m None and None",), "TC.s_m")

    def test_classmethod_tracing_log_records(self):
        value = TracedClass.class_method(None)

        self.assertEqual("TC.c_m None and None", value)
        self.assertEqual(2, len(list_handler.records))

        traced_function = \
            TracedClass.__dict__["class_method"].__func__.__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function, "test.dummy.TracedClass",
            ((None,), dict()), "TC.c_m")
        self._assert_return_record(
            list_handler.records[1], traced_function, "test.dummy.TracedClass",
            ("TC.c_m None and None",), "TC.c_m")

    def test_init_method_tracing_log_records(self):
        obj = TracedClass()

        self.assertEqual("TC.%s %s and %s", obj.format_string)
        self.assertEqual(1, len(list_handler.records))

        traced_function = TracedClass.__dict__["__init__"].__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function, "test.dummy.TracedClass",
            (tuple(), dict()), "TC.__i__")

    def test_call_method_tracing_log_records(self):
        obj = TracedClass()

        list_handler.reset()
        rv = obj()

        self.assertEqual("TC.__call__", rv)
        self.assertEqual(2, len(list_handler.records))

        traced_function = TracedClass.__dict__["__call__"].__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function, "test.dummy.TracedClass",
            (tuple(), dict()), "TC.__c__")
        self._assert_return_record(
            list_handler.records[1], traced_function, "test.dummy.TracedClass",
            ("TC.__call__",), "TC.__c__")

    def test_no_tracing_log_records_when_trace_disabled(self):
        dummy_module_logger.setLevel(logging.DEBUG)
        obj = TracedClass()

        self.assertEqual(0, len(list_handler.records))

    @unittest.skipUnless(
        hasattr(TracedClass.NestedClass, "__qualname__"),
        "__qualname__ is not available")
    def test_nested_classes_have_qualname_logger_name(self):
        self.assertEqual(
            "test.dummy.TracedClass.NestedClass",
            TracedClass.NestedClass.__dict__["__init__"]._tracing_proxy.logger.name)

    def test_nested_class_instance_method_tracing_log_records(self):
        obj = TracedClass.NestedClass()

        self.assertEqual("TC.NC.%s %s and %s", obj.format_string)
        self.assertEqual(1, len(list_handler.records))

        traced_function = \
            TracedClass.NestedClass.__dict__["__init__"].__wrapped__
        expected_logger_name = "test.dummy.%s" % getattr(
            TracedClass.NestedClass, "__qualname__", "NestedClass")
        self._assert_call_record(
            list_handler.records[0], traced_function, expected_logger_name,
            (tuple(), dict()), "TC.NC.__i__")

    def test_nested_internal_instance_method_tracing_log_records(self):
        value = TracedClass._TracedClass__InternalNestedClass().method(None)

        self.assertEqual("TC.__INC.m None and None", value)
        self.assertEqual(2, len(list_handler.records))

        traced_function = (
            TracedClass._TracedClass__InternalNestedClass.
                __dict__["method"].__wrapped__)
        expected_logger_name = "traced.testing.%s" % getattr(
            TracedClass._TracedClass__InternalNestedClass, "__qualname__",
            TracedClass._TracedClass__InternalNestedClass.__name__)
        self._assert_call_record(
            list_handler.records[0], traced_function, expected_logger_name,
            ((None,), dict()), "TC.__INC.m")
        self._assert_return_record(
            list_handler.records[1], traced_function, expected_logger_name,
            ("TC.__INC.m None and None",), "TC.__INC.m")

    def test_nested_internal_instance_method_tracing_log_records_when_enclosing_trace_disabled(self):
        dummy_module_logger.setLevel(logging.DEBUG)
        value = TracedClass._TracedClass__InternalNestedClass().method(None)

        self.assertEqual("TC.__INC.m None and None", value)
        self.assertEqual(2, len(list_handler.records))

    def test_no_nested_internal_instance_method_tracing_log_records_when_trace_disabled(self):
        named_tracer.setLevel(logging.DEBUG)
        value = TracedClass._TracedClass__InternalNestedClass().method(None)

        self.assertEqual("TC.__INC.m None and None", value)
        self.assertEqual(0, len(list_handler.records))


class TracedFunctionFunctionalTest(_TracedFunctionalTest):
    """Test the trace records emitted by an :func:`autologging.traced`
    decorated function.

    """

    def test_traced_function_tracing_log_records(self):
        nested_function = traced_function(None)

        self.assertEqual(2, len(list_handler.records))
        self._assert_call_record(
            list_handler.records[0], traced_function.__wrapped__, "test.dummy",
            ((None,), dict()), "t_f")
        self._assert_return_record(
            list_handler.records[1], traced_function.__wrapped__, "test.dummy",
            (nested_function,), "t_f")

    def test_no_traced_function_tracing_log_records_when_trace_disabled(self):
        dummy_module_logger.setLevel(logging.DEBUG)
        traced_function(None)

        self.assertEqual(0, len(list_handler.records))

    def test_nested_function_tracing_log_records(self):
        nested_function = traced_function(None)
        value = nested_function(None)

        self.assertEqual("t_f.n_f None and None", value)
        self.assertEqual(4, len(list_handler.records))
        self._assert_call_record(
            list_handler.records[2], nested_function.__wrapped__,
            "traced.testing", ((None,), dict()), "t_f.n_f")
        self._assert_return_record(
            list_handler.records[3], nested_function.__wrapped__,
            "traced.testing", ("t_f.n_f None and None",), "t_f.n_f")

    def test_nested_function_tracing_log_records_when_enclosing_trace_disabled(self):
        dummy_module_logger.setLevel(logging.DEBUG)
        nested_function = traced_function(None)

        self.assertEqual(0, len(list_handler.records))

        nested_function(None)
        self.assertEqual(2, len(list_handler.records))

    def test_no_nested_function_tracing_log_records_when_trace_disabled(self):
        named_tracer.setLevel(logging.DEBUG)
        nested_function = traced_function(None)

        self.assertEqual(2, len(list_handler.records))

        nested_function(None)
        self.assertEqual(2, len(list_handler.records))


def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(TracedClassFunctionalTest))
    suite.addTest(unittest.makeSuite(TracedFunctionFunctionalTest))

    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

