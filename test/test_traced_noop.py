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

"""Test case and runner for the :func:`autologging._traced_noop`
decorator function.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import _traced_noop, __version__

from test import named_tracer

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class SampleClass(object):

    def method(self):
        pass


_original_method_descriptor = SampleClass.__dict__["method"]


def sample_function():
    pass


_original_function = sample_function


class TracedNoopTest(unittest.TestCase):
    """Test the :func:`autologging._traced_noop` decorator function."""

    def test_noop_class(self):
        class_ = _traced_noop(SampleClass)
        self._assert_class(class_)

    def _assert_class(self, class_):
        self.assertFalse(
            hasattr(class_.__dict__["method"], "__autologging_traced__"))
        self.assertTrue(
            class_.__dict__["method"] is _original_method_descriptor)

    def test_noop_class_with_logger_arg(self):
        class_ = _traced_noop(named_tracer)(SampleClass)
        self._assert_class(class_)

    def test_noop_class_with_method_name_arg(self):
        class_ = _traced_noop("method")(SampleClass)
        self._assert_class(class_)

    def test_noop_class_with_logger_and_method_name_args(self):
        class_ = _traced_noop(named_tracer, "method")(SampleClass)
        self._assert_class(class_)

    def test_noop_function(self):
        func = _traced_noop(sample_function)
        self._assert_function(func)

    def _assert_function(self, func):
        self.assertFalse(hasattr(func, "__autologging_traced__"))
        self.assertTrue(func is _original_function)

    def test_noop_function_with_logger_arg(self):
        func = _traced_noop(named_tracer)(sample_function)
        self._assert_function(func)

    def test_noop_function_with_method_name_arg(self):
        # not a valid usage scenario, but it should still be tested, as
        # the original @traced will at least issue a warning
        func = _traced_noop("method")(sample_function)
        self._assert_function(func)

    def test_noop_function_with_logger_and_method_name_args(self):
        # not a valid usage scenario, but it should still be tested, as
        # the original @traced will at least issue a warning
        func = _traced_noop(named_tracer, "method")(sample_function)
        self._assert_function(func)


def suite():
    return unittest.makeSuite(TracedNoopTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

