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
:func:`autologging._make_traceable_staticmethod`.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import _make_traceable_staticmethod, TRACE, __version__

from test import list_handler, named_tracer

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class SampleClass(object):

    @staticmethod
    def method():
        pass


_original_method_descriptor = SampleClass.__dict__["method"]


class MakeTraceableStaticmethodTest(unittest.TestCase):
    """Test the :func:`autologging._make_traceable_staticmethod`
    function.

    """

    def setUp(self):
        list_handler.reset()
        named_tracer.setLevel(logging.NOTSET)

    def tearDown(self):
        if hasattr(
                SampleClass.__dict__["method"].__func__,
                "__autologging_traced__"):
            setattr(SampleClass, "method", _original_method_descriptor)

    def test_creates_delegator_descriptor(self):
        delegator = _make_traceable_staticmethod(
                SampleClass.__dict__["method"], named_tracer)

        self.assertTrue(delegator.__func__.__autologging_traced__)

    def test_wraps_original_unbound_function(self):
        delegator = _make_traceable_staticmethod(
                SampleClass.__dict__["method"], named_tracer)
        self.assertTrue(
                delegator.__func__.__wrapped__
                    is _original_method_descriptor.__func__)

    def test_uses_specified_logger(self):
        delegator = _make_traceable_staticmethod(
                SampleClass.__dict__["method"], named_tracer)

        self.assertTrue(
                delegator.__func__._tracing_proxy.logger is named_tracer)

    def test_with_trace_enabled_emits_log_records(self):
        named_tracer.setLevel(TRACE)
        delegator = _make_traceable_staticmethod(
            SampleClass.__dict__["method"], named_tracer)
        setattr(SampleClass, "method", delegator)
        SampleClass.method()

        self.assertEqual(2, len(list_handler.records))

        call_record = list_handler.records[0]
        self.assertEqual(
            delegator.__func__.__wrapped__.__name__, call_record.funcName)
        self.assertEqual("CALL *() **{}", call_record.getMessage())
        return_record = list_handler.records[1]
        self.assertEqual(
            delegator.__func__.__wrapped__.__name__, return_record.funcName)
        self.assertEqual("RETURN None", return_record.getMessage())

    def test_with_trace_disabled_does_not_emit_log_records(self):
        named_tracer.setLevel(logging.DEBUG)
        delegator = _make_traceable_staticmethod(
            SampleClass.__dict__["method"], named_tracer)
        SampleClass.method()
        self.assertEqual(0, len(list_handler.records))


def suite():
    return unittest.makeSuite(MakeTraceableStaticmethodTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

