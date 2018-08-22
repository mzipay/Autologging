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

"""Test case and runner for :func:`autologging._generate_logger_name`."""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import _generate_logger_name, __version__


class SampleClass(object):
    pass


def sample_function():
    pass


class GenerateLoggerNameTest(unittest.TestCase):
    """Test the :func:`autologging._generate_logger_name` function."""

    def test_default_name_for_class(self):
        self.assertEqual(
            "%s.SampleClass" % __name__, _generate_logger_name(SampleClass))

    def test_explicit_name_for_class(self):
        self.assertEqual(
            "my.channel.SampleClass",
            _generate_logger_name(SampleClass, parent_name = "my.channel"))

    def test_default_name_for_function(self):
        self.assertEqual(__name__, _generate_logger_name(sample_function))

    def test_explicit_name_for_function(self):
        self.assertEqual(
            "my.channel",
            _generate_logger_name(sample_function, parent_name = "my.channel"))


def suite():
    return unittest.makeSuite(GenerateLoggerNameTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

