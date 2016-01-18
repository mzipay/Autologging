# -*- coding: utf-8 -*-

# Copyright (c) 2013-2016 Matthew Zipay <mattz@ninthtest.net>
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

"""Test case and runner for :func:`autologging._make_call_record`."""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "1.0.0"

import logging
import unittest

from autologging import _make_call_record, TRACE


class SampleClass(object):

    def method(self):
        pass


class MakeCallRecordTest(unittest.TestCase):
    """Test the :func:`autologging._make_call_record` function."""

    def setUp(self):
        func = SampleClass.__dict__["method"]
        self._record = _make_call_record(
            __name__, "method", func.__code__.co_filename, 36, tuple(), dict())

    def test_creates_log_record(self):
        self.assertIsInstance(self._record, logging.LogRecord)

    def test_populates_log_record_name(self):
        self.assertEqual(__name__, self._record.name)

    def test_populates_log_record_msg(self):
        self.assertEqual("CALL *%r **%r", self._record.msg)

    def test_populates_log_record_args(self):
        self.assertEqual((tuple(), dict()), self._record.args)

    def test_populates_log_record_levelname(self):
        self.assertEqual("TRACE", self._record.levelname)

    def test_populates_log_record_levelno(self):
        self.assertEqual(TRACE, self._record.levelno)

    def test_populates_log_record_pathname(self):
        self.assertEqual(
            SampleClass.__dict__["method"].__code__.co_filename,
            self._record.pathname)

    def test_populates_log_record_lineno(self):
        self.assertEqual(36, self._record.lineno)

    def test_populates_log_record_funcName(self):
        self.assertEqual("method", self._record.funcName)


def suite():
    return unittest.makeSuite(MakeCallRecordTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

