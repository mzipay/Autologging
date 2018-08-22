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
decorator function, specifically as applied to a Python
`generator <https://docs.python.org/3/glossary.html#term-generator>`_.

See `issues/3 <https://github.com/mzipay/Autologging/issues/3>`_.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import TRACE, __version__

from test import (
    dummy_module_logger,
    get_dummy_lineno,
    list_handler,
    named_tracer,
)
from test.dummy import GeneratorClass, traced_generator
from test.functest_traced import _TracedFunctionalTest

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class _TracedGeneratorFunctionalTest(_TracedFunctionalTest):

    def _assert_yield_record(
            self, yield_record, traced_generator, expected_logger_name,
            expected_args, marker):
        self._assert_trace_record(
            yield_record, traced_generator, expected_logger_name,
            "YIELD %r", expected_args,
            get_dummy_lineno("#%s:LY" % marker))

    def _assert_stop_record(
            self, stop_record, traced_generator, expected_logger_name,
            marker):
        self._assert_trace_record(
            stop_record, traced_generator, expected_logger_name, "STOP",
            tuple(), get_dummy_lineno("#%s:LY" % marker))


class TracedGeneratorFunctionalTest(_TracedGeneratorFunctionalTest):
    """Test the trace records emitted by :func:`autologging.traced`
    generators.

    """

    def test_staticmethod_generator(self):
        geniter = GeneratorClass.static_generator("MZ")
        values = list(geniter)

        self.assertEqual(['Z', 'M'], values)
        self.assertEqual(5, len(list_handler.records))

        traced_function = \
            GeneratorClass.__dict__["static_generator"].__func__.__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function,
            "test.dummy.GeneratorClass", (("MZ",), dict()), "GC.s_g")
        self._assert_return_record(
            list_handler.records[1], traced_function,
            "test.dummy.GeneratorClass", (geniter.__wrapped__,), "GC.s_g")
        self._assert_yield_record(
            list_handler.records[2], traced_function,
            "test.dummy.GeneratorClass", ('Z',), "GC.s_g")
        self._assert_yield_record(
            list_handler.records[3], traced_function,
            "test.dummy.GeneratorClass", ('M',), "GC.s_g")
        self._assert_stop_record(
            list_handler.records[4], traced_function,
            "test.dummy.GeneratorClass", "GC.s_g")

    def test_classmethod_generator(self):
        geniter = GeneratorClass.class_generator("MZ")
        values = list(geniter)

        self.assertEqual(['Z', 'M'], values)
        self.assertEqual(5, len(list_handler.records))

        traced_function = \
            GeneratorClass.__dict__["class_generator"].__func__.__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function,
            "test.dummy.GeneratorClass", (("MZ",), dict()), "GC.c_g")
        self._assert_return_record(
            list_handler.records[1], traced_function,
            "test.dummy.GeneratorClass", (geniter.__wrapped__,), "GC.c_g")
        self._assert_yield_record(
            list_handler.records[2], traced_function,
            "test.dummy.GeneratorClass", ('Z',), "GC.c_g")
        self._assert_yield_record(
            list_handler.records[3], traced_function,
            "test.dummy.GeneratorClass", ('M',), "GC.c_g")
        self._assert_stop_record(
            list_handler.records[4], traced_function,
            "test.dummy.GeneratorClass", "GC.c_g")

    def test_method_generator(self):
        obj = GeneratorClass()
        geniter = obj.method_generator("MZ")
        values = list(geniter)

        self.assertEqual(['Z', 'M'], values)
        self.assertEqual(5, len(list_handler.records))

        traced_function = \
                GeneratorClass.__dict__["method_generator"].__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function,
            "test.dummy.GeneratorClass", (("MZ",), dict()), "GC.m_g")
        self._assert_return_record(
            list_handler.records[1], traced_function,
            "test.dummy.GeneratorClass", (geniter.__wrapped__,), "GC.m_g")
        self._assert_yield_record(
            list_handler.records[2], traced_function,
            "test.dummy.GeneratorClass", ('Z',), "GC.m_g")
        self._assert_yield_record(
            list_handler.records[3], traced_function,
            "test.dummy.GeneratorClass", ('M',), "GC.m_g")
        self._assert_stop_record(
            list_handler.records[4], traced_function,
            "test.dummy.GeneratorClass", "GC.m_g")

    def test_traced_function_generator(self):
        geniter = traced_generator("MZ")
        values = list(geniter)

        self.assertEqual(['Z', 'M'], values)
        self.assertEqual(5, len(list_handler.records))

        self._assert_call_record(
            list_handler.records[0], traced_generator.__wrapped__,
            "test.dummy", (("MZ",), dict()), "t_g")
        self._assert_return_record(
            list_handler.records[1], traced_generator.__wrapped__,
            "test.dummy", (geniter.__wrapped__,), "t_g")
        self._assert_yield_record(
            list_handler.records[2], traced_generator.__wrapped__,
            "test.dummy", ('Z',), "t_g")
        self._assert_yield_record(
            list_handler.records[3], traced_generator.__wrapped__,
            "test.dummy", ('M',), "t_g")
        self._assert_stop_record(
            list_handler.records[4], traced_generator.__wrapped__,
            "test.dummy", "t_g")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TracedGeneratorFunctionalTest))

    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

