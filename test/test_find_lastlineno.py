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

"""Test case and runner for :func:`autologging._find_lastlineno`."""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

from inspect import isgenerator
import logging
import unittest

from autologging import TRACE, _find_lastlineno, __version__

from test import get_lineno, has_co_lnotab

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


def sample_function(arg, keyword=None): #s_f:L1
    pass #s_f:LN


_f_filename = sample_function.__code__.co_filename
_expected_function_firstlineno = get_lineno(_f_filename, "#s_f:L1")
_expected_function_lastlineno = (
        get_lineno(_f_filename, "#s_f:LN")
        if has_co_lnotab else _expected_function_firstlineno)


class SampleClass(object):
    
    def method(self, arg, keyword=None): #SC.m:L1
        pass #SC.m:LN


_method = SampleClass.__dict__["method"]
_m_filename = _method.__code__.co_filename
_expected_method_firstlineno = get_lineno(_m_filename, "#SC.m:L1")
_expected_method_lastlineno = (
        get_lineno(_m_filename, "#SC.m:LN")
        if has_co_lnotab else _expected_method_firstlineno)


class FindLastLineNumberTest(unittest.TestCase):
    """Test the :func:`autologging._find_lastlineno` function."""

    def test_find_lastlineno_of_function(self):
        self.assertEqual(
            _expected_function_lastlineno,
            _find_lastlineno(sample_function.__code__))

    def test_find_lastlineno_of_method(self):
        self.assertEqual(
            _expected_method_lastlineno, _find_lastlineno(_method.__code__))


def suite():
    return unittest.makeSuite(FindLastLineNumberTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

