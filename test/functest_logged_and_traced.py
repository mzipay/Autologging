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

"""Functional test cases and runner for classes and functions that are
both ``@logged`` and ``@traced``.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import TRACE, __version__

from test import (
    dummy_module_logger,
    get_dummy_lineno,
    list_handler,
    named_logger,
    named_tracer,
)
from test.dummy import logged_and_traced_function, LoggedAndTracedClass

from test.functest_logged import _LoggedFunctionalTest
from test.functest_traced import _TracedFunctionalTest

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class _LoggedAndTracedFunctionalTest(
        _LoggedFunctionalTest, _TracedFunctionalTest):

    def setUp(self):
        dummy_module_logger.setLevel(TRACE)
        named_logger.setLevel(TRACE)
        named_tracer.setLevel(TRACE)
        list_handler.reset()


class LoggedAndTracedClassFunctionalTest(_LoggedAndTracedFunctionalTest):
    """Test the log and trace records for a class that has been
    decorated with **both** :func:`autologging.logged` and
    :func:`autologging.traced`.

    """

    def test_log_record_in_untraced_method(self):
        LoggedAndTracedClass()

        self.assertEqual(1, len(list_handler.records))

        init_function = LoggedAndTracedClass.__dict__["__init__"]
        self._assert_log_record(
            list_handler.records[0], init_function,
            "test.dummy.LoggedAndTracedClass", "LATC.__i__")

    def test_instance_method_log_and_trace_records(self):
        value = LoggedAndTracedClass().method(None)

        self.assertEqual("LATC.m None and None", value)
        self.assertEqual(4, len(list_handler.records))

        method_function = LoggedAndTracedClass.__dict__["method"].__wrapped__
        self._assert_call_record(
            list_handler.records[1], method_function,
            "test.dummy.LoggedAndTracedClass", ((None,), dict()), "LATC.m")
        self._assert_log_record(
            list_handler.records[2], method_function,
            "test.dummy.LoggedAndTracedClass", "LATC.m")
        self._assert_return_record(
            list_handler.records[3], method_function,
            "test.dummy.LoggedAndTracedClass", ("LATC.m None and None",),
            "LATC.m")

    def test_call_method_log_and_trace_records(self):
        obj = LoggedAndTracedClass.NestedClass()

        list_handler.reset()
        rv = obj("test")

        self.assertEqual("LATC.NC.__call__ test", rv)
        self.assertEqual(3, len(list_handler.records))

        wrapped_function = \
            LoggedAndTracedClass.NestedClass.__dict__["__call__"].__wrapped__
        qualname = getattr(
            LoggedAndTracedClass.NestedClass, "__qualname__", "NestedClass")
        expected_tracer_name = "test.dummy.%s" % qualname
        expected_logger_name = "logged.testing.%s" % qualname
        self._assert_call_record(
            list_handler.records[0], wrapped_function, expected_tracer_name,
            (("test",), dict()), "LATC.NC.__c__")
        self._assert_log_record(
            list_handler.records[1], wrapped_function, expected_logger_name,
            "LATC.NC.__c__")
        self._assert_return_record(
            list_handler.records[2], wrapped_function, expected_tracer_name,
            ("LATC.NC.__call__ test",), "LATC.NC.__c__")

    def test_instance_method_log_record_when_trace_disabled(self):
        dummy_module_logger.setLevel(logging.DEBUG)
        value = LoggedAndTracedClass().method(None)

        self.assertEqual("LATC.m None and None", value)
        self.assertEqual(2, len(list_handler.records))

        method_function = LoggedAndTracedClass.__dict__["method"].__wrapped__
        self._assert_log_record(
            list_handler.records[1], method_function,
            "test.dummy.LoggedAndTracedClass", "LATC.m")

    def test_instance_method_log_and_trace_records_when_both_disabled(self):
        dummy_module_logger.setLevel(logging.WARN)
        value = LoggedAndTracedClass().method(None)

        self.assertEqual("LATC.m None and None", value)
        self.assertEqual(0, len(list_handler.records))

    def test_nested_method_log_and_trace_records(self):
        LoggedAndTracedClass.NestedClass()

        self.assertEqual(2, len(list_handler.records))

        wrapped_function = \
            LoggedAndTracedClass.NestedClass.__dict__["__init__"].__wrapped__
        qualname = getattr(
            LoggedAndTracedClass.NestedClass, "__qualname__", "NestedClass")
        expected_tracer_name = "test.dummy.%s" % qualname
        expected_logger_name = "logged.testing.%s" % qualname
        self._assert_call_record(
            list_handler.records[0], wrapped_function, expected_tracer_name,
            (tuple(), dict()), "LATC.NC.__i__")
        self._assert_log_record(
            list_handler.records[1], wrapped_function, expected_logger_name,
            "LATC.NC.__i__")

    def test_nested_nonpublic_method_log_and_trace_records(self):
        LoggedAndTracedClass._NonPublicNestedClass()

        self.assertEqual(2, len(list_handler.records))

        wrapped_function = LoggedAndTracedClass._NonPublicNestedClass.__dict__[
            "__init__"].__wrapped__
        qualname = getattr(
            LoggedAndTracedClass._NonPublicNestedClass, "__qualname__",
            "_NonPublicNestedClass")
        expected_tracer_name = "traced.testing.%s" % qualname
        expected_logger_name = "test.dummy.%s" % qualname
        self._assert_call_record(
            list_handler.records[0], wrapped_function, expected_tracer_name,
            (tuple(), dict()), "LATC._NPNC.__i__")
        self._assert_log_record(
            list_handler.records[1], wrapped_function, expected_logger_name,
            "LATC._NPNC.__i__")

    def test_nested_internal_log_record_in_untraced_method(self):
        LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass()

        self.assertEqual(1, len(list_handler.records))

        init_function = (
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass.
                __dict__["__init__"])
        expected_logger_name = "logged.testing.%s" % getattr(
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass,
            "__qualname__",
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass.__name__)
        self._assert_log_record(
            list_handler.records[0], init_function, expected_logger_name,
            "LATC.__INC.__i__")

    def test_nested_internal_method_log_and_trace_records(self):
        obj = LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass()
        value = obj.method(None)

        self.assertEqual("LATC.__INC.m None and None", value)
        self.assertEqual(4, len(list_handler.records))

        wrapped_function = (
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass.
                __dict__["method"].__wrapped__)
        qualname = getattr(
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass,
            "__qualname__",
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass.__name__)
        expected_tracer_name = "traced.testing.%s" % qualname
        expected_logger_name = "logged.testing.%s" % qualname
        self._assert_call_record(
            list_handler.records[1], wrapped_function, expected_tracer_name,
            ((None,), dict()), "LATC.__INC.m")
        self._assert_log_record(
            list_handler.records[2], wrapped_function, expected_logger_name,
            "LATC.__INC.m")
        self._assert_return_record(
            list_handler.records[3], wrapped_function, expected_tracer_name,
            ("LATC.__INC.m None and None",), "LATC.__INC.m")

    def test_nested_internal_method_log_record_when_trace_disabled(self):
        named_tracer.setLevel(logging.DEBUG)
        obj = LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass()
        value = obj.method(None)

        self.assertEqual("LATC.__INC.m None and None", value)
        self.assertEqual(2, len(list_handler.records))

        wrapped_function = (
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass.
                __dict__["method"].__wrapped__)
        expected_logger_name = "logged.testing.%s" % getattr(
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass,
            "__qualname__",
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass.__name__)
        self._assert_log_record(
            list_handler.records[1], wrapped_function, expected_logger_name,
            "LATC.__INC.m")

    def test_nested_internal_method_trace_records_when_log_disabled(self):
        named_logger.setLevel(logging.WARN)
        obj = LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass()
        value = obj.method(None)

        self.assertEqual("LATC.__INC.m None and None", value)
        self.assertEqual(2, len(list_handler.records))

        wrapped_function = (
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass.
                __dict__["method"].__wrapped__)
        expected_tracer_name = "traced.testing.%s" % getattr(
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass,
            "__qualname__",
            LoggedAndTracedClass._LoggedAndTracedClass__InternalNestedClass.__name__)
        self._assert_call_record(
            list_handler.records[0], wrapped_function, expected_tracer_name,
            ((None,), dict()), "LATC.__INC.m")
        self._assert_return_record(
            list_handler.records[1], wrapped_function, expected_tracer_name,
            ("LATC.__INC.m None and None",), "LATC.__INC.m")


class LoggedAndTracedFunctionFunctionalTest(_LoggedAndTracedFunctionalTest):
    """Test the log and trace records for a function that has been
    decorated with **both** :func:`autologging.logged` and
    :func:`autologging.traced`.

    """

    def test_function_log_and_trace_records(self):
        nested_function = logged_and_traced_function(None)

        self.assertEqual(3, len(list_handler.records))

        wrapped_function = logged_and_traced_function.__wrapped__
        self._assert_call_record(
            list_handler.records[0], wrapped_function, "traced.testing",
            ((None,), dict()), "l_a_t_f")
        self._assert_log_record(
            list_handler.records[1], wrapped_function, "test.dummy", "l_a_t_f")
        self._assert_return_record(
            list_handler.records[2], wrapped_function, "traced.testing",
            (nested_function,), "l_a_t_f")

    def test_function_log_record_when_trace_disabled(self):
        named_tracer.setLevel(logging.DEBUG)
        nested_function = logged_and_traced_function(None)

        self.assertEqual(1, len(list_handler.records))

        wrapped_function = logged_and_traced_function.__wrapped__
        self._assert_log_record(
            list_handler.records[0], wrapped_function, "test.dummy", "l_a_t_f")

    def test_function_trace_records_when_log_disabled(self):
        dummy_module_logger.setLevel(logging.WARN)
        nested_function = logged_and_traced_function(None)

        self.assertEqual(2, len(list_handler.records))

        wrapped_function = logged_and_traced_function.__wrapped__
        self._assert_call_record(
            list_handler.records[0], wrapped_function, "traced.testing",
            ((None,), dict()), "l_a_t_f")
        self._assert_return_record(
            list_handler.records[1], wrapped_function, "traced.testing",
            (nested_function,), "l_a_t_f")

    def test_nested_function_log_and_trace_records(self):
        nested_function = logged_and_traced_function(None)
        value = nested_function(None)

        self.assertEqual("l_a_t_f.n_t_a_l_f None and None", value)
        self.assertEqual(6, len(list_handler.records))

        wrapped_function = nested_function.__wrapped__
        self._assert_call_record(
            list_handler.records[3], wrapped_function, "test.dummy",
            ((None,), dict()), "l_a_t_f.n_t_a_l_f")
        self._assert_log_record(
            list_handler.records[4], wrapped_function, "logged.testing",
            "l_a_t_f.n_t_a_l_f")
        self._assert_return_record(
            list_handler.records[5], wrapped_function, "test.dummy",
            ("l_a_t_f.n_t_a_l_f None and None",), "l_a_t_f.n_t_a_l_f")

    def test_nested_function_log_record_when_trace_disabled(self):
        dummy_module_logger.setLevel(logging.DEBUG)
        nested_function = logged_and_traced_function(None)
        value = nested_function(None)

        self.assertEqual("l_a_t_f.n_t_a_l_f None and None", value)
        self.assertEqual(4, len(list_handler.records))

        wrapped_function = nested_function.__wrapped__
        self._assert_log_record(
            list_handler.records[3], wrapped_function, "logged.testing",
            "l_a_t_f.n_t_a_l_f")

    def test_nested_function_trace_records_when_log_disabled(self):
        named_logger.setLevel(logging.WARN)
        nested_function = logged_and_traced_function(None)
        value = nested_function(None)

        self.assertEqual("l_a_t_f.n_t_a_l_f None and None", value)
        self.assertEqual(5, len(list_handler.records))

        wrapped_function = nested_function.__wrapped__
        self._assert_call_record(
            list_handler.records[3], wrapped_function, "test.dummy",
            ((None,), dict()), "l_a_t_f.n_t_a_l_f")
        self._assert_return_record(
            list_handler.records[4], wrapped_function, "test.dummy",
            ("l_a_t_f.n_t_a_l_f None and None",), "l_a_t_f.n_t_a_l_f")


def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(LoggedAndTracedClassFunctionalTest))
    suite.addTest(unittest.makeSuite(LoggedAndTracedFunctionFunctionalTest))

    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

