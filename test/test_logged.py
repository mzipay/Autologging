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

"""Test case and runner for the :func:`autologging.logged` decorator
function.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import os
import unittest

from autologging import logged, __version__

from test import named_logger

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class SampleClass(object):
    pass


def sample_function():
    pass


class LoggedTest(unittest.TestCase):
    """Test the :func:`autologging.logged` decorator function."""

    def tearDown(self):
        if hasattr(SampleClass, "_SampleClass__log"):
            delattr(SampleClass, "_SampleClass__log")
        if hasattr(sample_function, "_log"):
            delattr(sample_function, "_log")

    def test_logged_class_uses_default_logger(self):
        logged(SampleClass)

        self.assertEqual(
            __name__ + ".SampleClass", SampleClass._SampleClass__log.name)

    def test_logged_class_uses_named_logger(self):
        logged(named_logger)(SampleClass)

        self.assertEqual(
            named_logger.name + ".SampleClass",
            SampleClass._SampleClass__log.name)

    def test_logged_function_uses_default_logger(self):
        logged(sample_function)

        self.assertEqual(__name__, sample_function._log.name)

    def test_logged_class_uses_named_logger(self):
        logged(named_logger)(sample_function)

        self.assertEqual(named_logger.name, sample_function._log.name)


def suite():
    return unittest.makeSuite(LoggedTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

