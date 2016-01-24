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

"""Test case and runner for
:func:`autologging._create_log_record_factories`.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "1.0.0"

import unittest

from autologging import _create_log_record_factories

from test import has_co_lnotab


class SampleClass(object):
    
    def method(self):
        pass


_func = SampleClass.__dict__["method"]
_expected_call_args = (__name__, "method", _func.__code__.co_filename, 40)
_expected_return_args = (
    __name__, "method", _func.__code__.co_filename,
    41 if has_co_lnotab else 40)


class CreateLogRecordFactoriesTest(unittest.TestCase):
    """Test the :func:`autologging._create_log_record_factories
    function.

    """
    
    def test_creates_call_record_factory(self):
        make_call_record, _ = _create_log_record_factories(
            __name__, SampleClass.__dict__["method"])
        self.assertEqual(_expected_call_args, make_call_record.args)

    def test_creates_return_record_factory(self):
        _, make_return_record = _create_log_record_factories(
            __name__, SampleClass.__dict__["method"])
        self.assertEqual(_expected_return_args, make_return_record.args)


def suite():
    return unittest.makeSuite(CreateLogRecordFactoriesTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

