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

"""Test case and runner for :func:`autologging._add_logger_to`."""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import _add_logger_to, __version__

from test import named_logger


class SampleClass(object):
    pass


def sample_function():
    pass


class AddLoggerToTest(unittest.TestCase):
    """Test the :func:`autologging._add_logger_to` function."""

    def tearDown(self):
        if hasattr(SampleClass, "_SampleClass__log"):
            delattr(SampleClass, "_SampleClass__log")
        if hasattr(sample_function, "_log"):
            delattr(sample_function, "_log")

    def test_add_default_logger_to_class(self):
        self.assertFalse(hasattr(SampleClass, "_SampleClass__log"))
        _add_logger_to(SampleClass)
        self.assertEqual(
            "%s.SampleClass" % __name__, SampleClass._SampleClass__log.name)

    def test_add_named_logger_to_class(self):
        self.assertFalse(hasattr(SampleClass, "_SampleClass__log"))
        _add_logger_to(SampleClass, logger_name = named_logger.name)
        self.assertEqual(named_logger.name, SampleClass._SampleClass__log.name)

    def test_add_default_logger_to_function(self):
        self.assertFalse(hasattr(sample_function, "_log"))
        _add_logger_to(sample_function)
        self.assertEqual(__name__, sample_function._log.name)

    def test_add_named_logger_to_function(self):
        self.assertFalse(hasattr(sample_function, "_log"))
        _add_logger_to(sample_function, logger_name = named_logger.name)
        self.assertEqual(named_logger.name, sample_function._log.name)


def suite():
    return unittest.makeSuite(AddLoggerToTest)

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

