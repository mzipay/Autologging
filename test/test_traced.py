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

"""Test case and runner for the :func:`autologging.traced` decorator
function.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import TRACE, traced, __version__

from test import named_tracer

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class SampleClass(object):

    def __init__(self):
        pass


_original_method_descriptor = SampleClass.__dict__["__init__"]


def sample_function():
    pass


class TracedTest(unittest.TestCase):
    """Test the :func:`autologging.traced` decorator function."""

    def tearDown(self):
        setattr(SampleClass, "__init__", _original_method_descriptor)

    def test_traced_with_empty_args_is_equivalent_to_traced(self):
        self.assertTrue(traced() is traced)

    def test_traced_does_not_replace_class(self):
        self.assertTrue(traced(SampleClass) is SampleClass)

    def test_traced_class_uses_default_logger(self):
        traced(SampleClass)

        self.assertEqual(
            __name__ + ".SampleClass",
            SampleClass.__dict__["__init__"]._tracing_proxy.logger.name)

    def test_traced_class_uses_named_logger(self):
        traced(named_tracer)(SampleClass)

        self.assertEqual(
            named_tracer.name + ".SampleClass",
            SampleClass.__dict__["__init__"]._tracing_proxy.logger.name)

    def test_traced_replaces_function(self):
        traced_sample_function = traced(sample_function)

        self.assertFalse(traced_sample_function is sample_function)

    def test_replaced_function_is_wrapped(self):
        traced_sample_function = traced(sample_function)

        self.assertTrue(traced_sample_function.__wrapped__ is sample_function)

    def test_traced_function_uses_default_logger(self):
        traced_sample_function = traced(sample_function)

        self.assertEqual(
            __name__, traced_sample_function._tracing_proxy.logger.name)

    def test_traced_function_uses_named_logger(self):
        traced_sample_function = traced(named_tracer)(sample_function)

        self.assertEqual(
            named_tracer.name,
            traced_sample_function._tracing_proxy.logger.name)


def suite():
    return unittest.makeSuite(TracedTest)

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

