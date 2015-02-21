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

"""Test cases and runner for the :func:`autologging.TracedMethods`
metaclass factory.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.4.0"

import logging
import os
import sys
import unittest

from autologging import AutologgingProxyDescriptor, _is_private, _mangle, TRACE
from test import list_handler, named_tracer
from test.dummy import (
    _TracedParent,
    dummyM_module_logger,
    get_dummyM_lineno,
    ModuleLoggerExplicitTracedClass,
    ModuleLoggerImplicitSpecialTracedClass,
    ModuleLoggerImplicitTracedClass,
    NamedTracerExplicitTracedClass,
    NamedTracerImplicitSpecialTracedClass,
    NamedTracerImplicitTracedClass,
    NonTracedChildTracedParent,
    TracedChildNonTracedParent,
    TracedChildTracedParent,
)

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


def _get_logger_name(class_):
    parent_logger_name = (
        dummyM_module_logger.name if ("ModuleLogger" in class_.__name__)
        else named_tracer.name)
    expected_logger_name = "%s.%s" % (
        parent_logger_name,
        getattr(class_, "__qualname__", class_.__name__))
    return expected_logger_name


def _get_pathname(method):
    if (hasattr(method, "__wrapped__")):
        return method.__wrapped__.__code__.co_filename
    else:
        return method.__code__.co_filename


def _get_traced_method_names(class_):
    return [name for (name, value) in class_.__dict__.items()
            if isinstance(value, AutologgingProxyDescriptor)]


def _get_logger_delegator(traced_method):
    # the logger delegators are free variables of the tracing proxy function
    # closures
    var_index = traced_method.__code__.co_freevars.index("logger_delegator")
    return traced_method.__closure__[var_index].cell_contents


class TracedMethodsTest(unittest.TestCase):

    _FIXTURE = {
        ModuleLoggerImplicitTracedClass: {
            "log_record_fields": {
                "name": _get_logger_name(ModuleLoggerImplicitTracedClass),
                "pathname":
                    _get_pathname(ModuleLoggerImplicitTracedClass.method),
            },
            "traced_method_names": {
                "static_method": ["#MLITC.s_m:L1", "#MLITC.s_m:LN"],
                "class_method": ["#MLITC.c_m:L1", "#MLITC.c_m:LN"],
                "__init__": ["#MLITC.__i__:L1", "#MLITC.__i__:LN"],
                "method": ["#MLITC.m:L1", "#MLITC.m:LN"],
            },
        },
        ModuleLoggerImplicitTracedClass.NestedNamedTracerExplicitTracedClass: {
            "log_record_fields": {
                "name": _get_logger_name(
                    ModuleLoggerImplicitTracedClass.NestedNamedTracerExplicitTracedClass),
                "pathname": _get_pathname(
                    ModuleLoggerImplicitTracedClass.NestedNamedTracerExplicitTracedClass.method),
            },
            "traced_method_names": {
                "class_method": ["#MLITC.NNTETC.c_m:L1",
                                 "#MLITC.NNTETC.c_m:LN"],
                "method": ["#MLITC.NNTETC.m:L1", "#MLITC.NNTETC.m:LN"],
            },
        },
        ModuleLoggerImplicitSpecialTracedClass: {
            "log_record_fields": {
                "name": _get_logger_name(ModuleLoggerImplicitSpecialTracedClass),
                "pathname": _get_pathname(
                    ModuleLoggerImplicitSpecialTracedClass.method),
            },
            "traced_method_names": {
                "__init__": ["#MLISTC.__i__:L1", "#MLISTC.__i__:LN"],
                "method": ["#MLISTC.m:L1", "#MLISTC.m:LN"],
                "_nonpublic": ["#MLISTC._n:L1", "#MLISTC._n:LN"],
                "__private": ["#MLISTC.__p:L1", "#MLISTC.__p:LN"],
                "__eq__": ["#MLISTC.__e__:L1", "#MLISTC.__e__:LN"],
            },
        },
        ModuleLoggerExplicitTracedClass: {
            "log_record_fields": {
                "name": _get_logger_name(ModuleLoggerExplicitTracedClass),
                "pathname":
                    _get_pathname(ModuleLoggerExplicitTracedClass.method),
            },
            "traced_method_names": {
                "static_method": ["#MLETC.s_m:L1", "#MLETC.s_m:LN"],
                "__init__": ["#MLETC.__i__:L1", "#MLETC.__i__:LN"],
                "_nonpublic": ["#MLETC._n:L1", "#MLETC._n:LN"],
                "__private": ["#MLETC.__p:L1", "#MLETC.__p:LN"],
            },
        },
        NamedTracerImplicitTracedClass: {
            "log_record_fields": {
                "name": _get_logger_name(NamedTracerImplicitTracedClass),
                "pathname":
                    _get_pathname(NamedTracerImplicitTracedClass.method),
            },
            "traced_method_names": {
                "static_method": ["#NTITC.s_m:L1", "#NTITC.s_m:LN"],
                "class_method": ["#NTITC.c_m:L1", "#NTITC.c_m:LN"],
                "__init__": ["#NTITC.__i__:L1", "#NTITC.__i__:LN"],
                "method": ["#NTITC.m:L1", "#NTITC.m:LN"],
            },
        },
        NamedTracerImplicitTracedClass.NestedModuleLoggerExplicitTracedClass: {
            "log_record_fields": {
                "name": _get_logger_name(
                    NamedTracerImplicitTracedClass.NestedModuleLoggerExplicitTracedClass),
                "pathname": _get_pathname(
                    NamedTracerImplicitTracedClass.NestedModuleLoggerExplicitTracedClass.method),
            },
            "traced_method_names": {
                "static_method": ["#NTITC.NMLETC.s_m:L1",
                                  "#NTITC.NMLETC.s_m:LN"],
                "method": ["#NTITC.NMLETC.m:L1", "#NTITC.NMLETC.m:LN"],
            },
        },
        NamedTracerImplicitSpecialTracedClass: {
            "log_record_fields": {
                "name":
                    _get_logger_name(NamedTracerImplicitSpecialTracedClass),
                "pathname": _get_pathname(
                    NamedTracerImplicitSpecialTracedClass.method),
            },
            "traced_method_names": {
                "method": ["#NTISTC.m:L1", "#NTISTC.m:LN"],
                "_nonpublic": ["#NTISTC._n:L1", "#NTISTC._n:LN"],
                "__private": ["#NTISTC.__p:L1", "#NTISTC.__p:LN"],
                "__eq__": ["#NTISTC.__e__:L1", "#NTISTC.__e__:LN"],
            },
        },
        NamedTracerExplicitTracedClass: {
            "log_record_fields": {
                "name": _get_logger_name(NamedTracerExplicitTracedClass),
                "pathname":
                    _get_pathname(NamedTracerExplicitTracedClass.method),
            },
            "traced_method_names": {
                "class_method": ["#NTETC.c_m:L1", "#NTETC.c_m:LN"],
                "_nonpublic": ["#NTETC._n:L1", "#NTETC._n:LN"],
                "__private": ["#NTETC.__p:L1", "#NTETC.__p:LN"],
                "__eq__": ["#NTETC.__e__:L1", "#NTETC.__e__:LN"],
            },
        },
    }

    @classmethod
    def setUpClass(cls):
        dummyM_module_logger.setLevel(TRACE)

    def setUp(self):
        list_handler.reset()
        self._fixture = None

    def test_ModuleLoggerImplicitTracedClass(self):
        self._fixture = self._FIXTURE[ModuleLoggerImplicitTracedClass]
        self._assert_traced_class(ModuleLoggerImplicitTracedClass)

    def test_NestedNamedTracerExplicitTracedClass(self):
        self._fixture = self._FIXTURE[
            ModuleLoggerImplicitTracedClass.NestedNamedTracerExplicitTracedClass]
        self._assert_traced_class(
            ModuleLoggerImplicitTracedClass.NestedNamedTracerExplicitTracedClass)

    def test_ModuleLoggerImplicitSpecialTracedClass(self):
        self._fixture = self._FIXTURE[ModuleLoggerImplicitSpecialTracedClass]
        self._assert_traced_class(ModuleLoggerImplicitSpecialTracedClass)

    def test_ModuleLoggerExplicitTracedClass(self):
        self._fixture = self._FIXTURE[ModuleLoggerExplicitTracedClass]
        self._assert_traced_class(ModuleLoggerExplicitTracedClass)

    def test_NamedTracerImplicitTracedClass(self):
        self._fixture = self._FIXTURE[NamedTracerImplicitTracedClass]
        self._assert_traced_class(NamedTracerImplicitTracedClass)

    def test_NestedModuleLoggerExplicitTracedClass(self):
        self._fixture = self._FIXTURE[
            NamedTracerImplicitTracedClass.NestedModuleLoggerExplicitTracedClass]
        self._assert_traced_class(
            NamedTracerImplicitTracedClass.NestedModuleLoggerExplicitTracedClass)

    def test_NamedTracerImplicitSpecialTracedClass(self):
        self._fixture = self._FIXTURE[NamedTracerImplicitSpecialTracedClass]
        self._assert_traced_class(NamedTracerImplicitSpecialTracedClass)

    def test_NamedTracerExplicitTracedClass(self):
        self._fixture = self._FIXTURE[NamedTracerExplicitTracedClass]
        self._assert_traced_class(NamedTracerExplicitTracedClass)

    def test_NonTracedChildTracedParent(self):
        self.assertEqual([],
            _get_traced_method_names(NonTracedChildTracedParent))

        obj = NonTracedChildTracedParent()
        self.assertEqual("INSTANCE", obj.method())

        self.assertEqual(4, len(list_handler.records))

        parent_method_return_record = list_handler.records.pop()
        expected_record = logging.LogRecord(
            "%s._TracedParent" % dummyM_module_logger.name,
            TRACE,
            obj.method.__code__.co_filename,
            get_dummyM_lineno("#_TP.m:LN"),
            "RETURN %r",
            ("instance",),
            None,
            func="method"
        )
        self._compare_log_records(expected_record, parent_method_return_record)

        parent_method_call_record = list_handler.records.pop()
        expected_record.lineno = get_dummyM_lineno("#_TP.m:L1")
        expected_record.msg = "CALL *%r **%r"
        expected_record.args = (tuple(), dict())
        self._compare_log_records(expected_record, parent_method_call_record)

        parent_init_return_record = list_handler.records.pop()
        expected_record.funcName = "__init__"
        expected_record.lineno = get_dummyM_lineno("#_TP.__i__:LN")
        expected_record.msg = "RETURN %r"
        expected_record.args = (None,)
        self._compare_log_records(expected_record, parent_init_return_record)

        parent_init_call_record = list_handler.records.pop()
        expected_record.lineno = get_dummyM_lineno("#_TP.__i__:L1")
        expected_record.msg = "CALL *%r **%r"
        expected_record.args = (tuple(), dict())
        self._compare_log_records(expected_record, parent_init_call_record)

    def test_TracedChildNonTracedParent(self):
        self.assertEqual(["method"],
            _get_traced_method_names(TracedChildNonTracedParent))

        obj = TracedChildNonTracedParent()
        self.assertEqual("INSTANCE", obj.method())

        self.assertEqual(2, len(list_handler.records))

        child_method_return_record = list_handler.records.pop()
        expected_record = logging.LogRecord(
            "%s.TracedChildNonTracedParent" % dummyM_module_logger.name,
            TRACE,
            obj.method.__wrapped__.__code__.co_filename,
            get_dummyM_lineno("#TCNTP.m:LN"),
            "RETURN %r",
            ("INSTANCE",),
            None,
            func="method"
        )
        self._compare_log_records(expected_record, child_method_return_record)

        child_method_call_record = list_handler.records.pop()
        expected_record.lineno = get_dummyM_lineno("#TCNTP.m:L1")
        expected_record.msg = "CALL *%r **%r"
        expected_record.args = (tuple(), dict())
        self._compare_log_records(expected_record, child_method_call_record)

    def test_TracedChildTracedParent(self):
        self.assertEqual(["method"],
            _get_traced_method_names(TracedChildTracedParent))

        obj = TracedChildTracedParent()
        self.assertEqual("INSTANCE", obj.method())

        self.assertEqual(6, len(list_handler.records))

        child_method_return_record = list_handler.records.pop()
        expected_record = logging.LogRecord(
            "%s.TracedChildTracedParent" % dummyM_module_logger.name,
            TRACE,
            obj.method.__wrapped__.__code__.co_filename,
            get_dummyM_lineno("#TCTP.m:LN"),
            "RETURN %r",
            ("INSTANCE",),
            None,
            func="method"
        )
        self._compare_log_records(expected_record, child_method_return_record)

        parent_method_return_record = list_handler.records.pop()
        expected_record.name = "%s._TracedParent" % dummyM_module_logger.name
        expected_record.lineno = get_dummyM_lineno("#_TP.m:LN")
        expected_record.args = ("instance",)
        self._compare_log_records(expected_record, parent_method_return_record)

        parent_method_call_record = list_handler.records.pop()
        expected_record.lineno = get_dummyM_lineno("#_TP.m:L1")
        expected_record.msg = "CALL *%r **%r"
        expected_record.args = (tuple(), dict())
        self._compare_log_records(expected_record, parent_method_call_record)

        child_method_call_record = list_handler.records.pop()
        expected_record.name = \
            "%s.TracedChildTracedParent" % dummyM_module_logger.name
        expected_record.lineno = get_dummyM_lineno("#TCTP.m:L1")
        self._compare_log_records(expected_record, child_method_call_record)

        parent_init_return_record = list_handler.records.pop()
        expected_record.name = "%s._TracedParent" % dummyM_module_logger.name
        expected_record.lineno = get_dummyM_lineno("#_TP.__i__:LN")
        expected_record.msg = "RETURN %r"
        expected_record.args = (None,)
        expected_record.funcName = "__init__"
        self._compare_log_records(expected_record, parent_init_return_record)

        parent_init_call_record = list_handler.records.pop()
        expected_record.lineno = get_dummyM_lineno("#_TP.__i__:L1")
        expected_record.msg = "CALL *%r **%r"
        expected_record.args = (tuple(), dict())
        self._compare_log_records(expected_record, parent_init_call_record)

    def _compare_log_records(self, expected_record, actual_record):
        self.assertEqual(expected_record.name, actual_record.name)
        self.assertEqual(expected_record.levelname, actual_record.levelname)
        self.assertEqual(expected_record.levelno, actual_record.levelno)
        self.assertEqual(expected_record.pathname, actual_record.pathname)
        self.assertEqual(expected_record.lineno, actual_record.lineno)
        self.assertEqual(expected_record.funcName, actual_record.funcName)
        self.assertEqual(expected_record.getMessage(), actual_record.getMessage())

    def _assert_traced_class(self, class_):
        self._assert_traced_method_names(class_)
        self._assert_logger_delegator(class_)
        self._assert_traced_method_log_records(class_)

    def _assert_traced_method_names(self, class_):
        expected_method_names = [
            name if (not _is_private(name)) else _mangle(name, class_.__name__)
            for name in self._fixture["traced_method_names"]]
        actual_method_names = _get_traced_method_names(class_)
        self.assertEqual(sorted(expected_method_names),
                         sorted(actual_method_names))

    def _assert_logger_delegator(self, class_):
        expected_logger_name = self._fixture["log_record_fields"]["name"]
        for method_name in self._fixture["traced_method_names"]:
            if (_is_private(method_name)):
                method_name = _mangle(method_name, class_.__name__)
            method = getattr(class_, method_name)
            logger_delegator = _get_logger_delegator(method)
            self.assertEqual(expected_logger_name, logger_delegator.name)
            self.assertEqual(TRACE, logger_delegator.getEffectiveLevel())

    def _assert_traced_method_log_records(self, class_):
        method_names = self._fixture["traced_method_names"]

        obj = class_()

        if ("__init__" in method_names):
            self.assertEqual(2, len(list_handler.records))
            self._assert_init_log_records()

        if ("__eq__" in method_names):
            self.assertFalse(obj == None)
            self.assertEqual(2, len(list_handler.records))
            self._assert_eq_log_records()

        for method_name in [name for name in method_names
                            if (name not in ["__init__", "__eq__"])]:
            if (not _is_private(method_name)):
                method = getattr(obj, method_name)
            else:
                method = getattr(obj, _mangle(method_name, class_.__name__))

            self.assertEqual("spam and eggs", method("spam", keyword="eggs"))
            self.assertEqual(2, len(list_handler.records))

            self._assert_return_log_record(method_name)
            self._assert_call_log_record(method_name)

    def _assert_init_log_records(self):
        expected_logger_name = self._fixture["log_record_fields"]["name"]
        expected_pathname = self._fixture["log_record_fields"]["pathname"]
        expected_linenos = self._fixture["traced_method_names"]["__init__"]

        return_record = list_handler.records.pop()
        expected_record = logging.LogRecord(
            expected_logger_name,
            TRACE,
            expected_pathname,
            get_dummyM_lineno(expected_linenos[1]),
            "RETURN %r",
            (None,),
            None,
            func="__init__"
        )
        self._compare_log_records(expected_record, return_record)

        call_record = list_handler.records.pop()
        expected_record.lineno = get_dummyM_lineno(expected_linenos[0])
        expected_record.msg = "CALL *%r **%r"
        expected_record.args = (tuple(), dict())
        self._compare_log_records(expected_record, call_record)

    def _assert_eq_log_records(self):
        expected_logger_name = self._fixture["log_record_fields"]["name"]
        expected_pathname = self._fixture["log_record_fields"]["pathname"]
        expected_linenos = self._fixture["traced_method_names"]["__eq__"]

        return_record = list_handler.records.pop()
        expected_record = logging.LogRecord(
            expected_logger_name,
            TRACE,
            expected_pathname,
            get_dummyM_lineno(expected_linenos[1]),
            "RETURN %r",
            (False,),
            None,
            func="__eq__"
        )
        self._compare_log_records(expected_record, return_record)

        call_record = list_handler.records.pop()
        expected_record.lineno = get_dummyM_lineno(expected_linenos[0])
        expected_record.msg = "CALL *%r **%r"
        expected_record.args = ((None,), dict())
        self._compare_log_records(expected_record, call_record)

    def _assert_return_log_record(self, expected_method_name):
        expected_logger_name = self._fixture["log_record_fields"]["name"]
        expected_pathname = self._fixture["log_record_fields"]["pathname"]
        expected_lineno = \
            self._fixture["traced_method_names"][expected_method_name][1]

        return_record = list_handler.records.pop()
        expected_record = logging.LogRecord(
            expected_logger_name,
            TRACE,
            expected_pathname,
            get_dummyM_lineno(expected_lineno),
            "RETURN %r",
            ("spam and eggs",),
            None,
            func=expected_method_name
        )
        self._compare_log_records(expected_record, return_record)

    def _assert_call_log_record(self, expected_method_name):
        expected_logger_name = self._fixture["log_record_fields"]["name"]
        expected_pathname = self._fixture["log_record_fields"]["pathname"]
        expected_lineno = \
            self._fixture["traced_method_names"][expected_method_name][0]

        call_record = list_handler.records.pop()
        expected_record = logging.LogRecord(
            expected_logger_name,
            TRACE,
            expected_pathname,
            get_dummyM_lineno(expected_lineno),
            "CALL *%r **%r",
            (("spam",), {"keyword": "eggs"}),
            None,
            func=expected_method_name
        )
        self._compare_log_records(expected_record, call_record)


def suite():
    """Build the test suite for :func:`autologging.TracedMethods`."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TracedMethodsTest))

    return suite


if (__name__ == "__main__"):
    unittest.TextTestRunner().run(suite())

