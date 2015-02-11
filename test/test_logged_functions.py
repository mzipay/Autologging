# -*- coding: utf-8 -*-

# Copyright (c) 2013 Matthew Zipay <mattz@ninthtest.net>
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

"""Test cases and runner for the :func:`autologging.logged` decorator
function.

"""

__author__ = "Simon Knopp <simon.knopp@pg.canterbury.ac.nz>"
__version__ = "0.1"

import logging
import os
import unittest

from test import ListHandler
from test.loggedfunctions import (module_logger_fn, named_logger_fn,
                                  outer_fn, _internal_fn)

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class ModuleLoggerLoggedTest(unittest.TestCase):
    """Test :func:`autologging.logged` using the default (module) logger."""

    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger("test.loggedfunctions.module_logger_fn")
        logger.setLevel(logging.DEBUG)
        cls._handler = ListHandler(level=logging.DEBUG)
        logger.addHandler(cls._handler)
        cls.expected_name = "test.loggedfunctions.module_logger_fn"
        cls.expected_levelname = "INFO"
        cls.expected_levelno = logging.INFO
        cls.expected_pathname = \
            module_logger_fn.__code__.co_filename  # @UndefinedVariable
        cls.expected_filename = os.path.basename(cls.expected_pathname)
        cls.expected_module = os.path.splitext(cls.expected_filename)[0]

    def test_call(self):
        module_logger_fn()
        record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, record.name)
        self.assertEqual(self.expected_levelname, record.levelname)
        self.assertEqual(self.expected_levelno, record.levelno)
        self.assertEqual(self.expected_pathname, record.pathname)
        self.assertEqual(self.expected_filename, record.filename)
        self.assertEqual(self.expected_module, record.module)
        self.assertEqual(39, record.lineno)
        self.assertEqual("module_logger_fn", record.funcName)
        self.assertEqual("module_logger_fn test.", record.getMessage())


class NamedLoggerLoggedTest(unittest.TestCase):
    """Test :func:`autologging.logged` using a user-named logger."""

    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger("logged.testing.named_logger_fn")
        logger.setLevel(logging.DEBUG)
        cls._handler = ListHandler(level=logging.DEBUG)
        logger.addHandler(cls._handler)
        cls.expected_name = "logged.testing.named_logger_fn"
        cls.expected_levelname = "INFO"
        cls.expected_levelno = logging.INFO
        cls.expected_pathname = \
            named_logger_fn.__code__.co_filename  # @UndefinedVariable
        cls.expected_filename = os.path.basename(cls.expected_pathname)
        cls.expected_module = os.path.splitext(cls.expected_filename)[0]

    def test_call(self):
        named_logger_fn()
        record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, record.name)
        self.assertEqual(self.expected_levelname, record.levelname)
        self.assertEqual(self.expected_levelno, record.levelno)
        self.assertEqual(self.expected_pathname, record.pathname)
        self.assertEqual(self.expected_filename, record.filename)
        self.assertEqual(self.expected_module, record.module)
        self.assertEqual(48, record.lineno)
        self.assertEqual("named_logger_fn", record.funcName)
        self.assertEqual("named_logger_fn test.", record.getMessage())


class OuterFuncTest(unittest.TestCase):
    """Test :func:`autologging.logged` on a nested function."""

    def test_inner_logger(self):
        self.assertTrue(hasattr(outer_fn(), "__logger"))

    def test_inner_fn_logger_not_in_outer_fn(self):
        self.assertFalse(hasattr(outer_fn, "__logger"))

    def test_inner_fn_logger_name(self):
        inner_fn = outer_fn()
        if (hasattr(inner_fn, "__qualname__")):
            expected_name = "test.loggedfunctions.outer_fn.<locals>.inner_fn"
        else:
            expected_name = "test.loggedfunctions.inner_fn"
        self.assertEqual(expected_name,
                         getattr(inner_fn, "__logger").name)
        self.assertEqual(expected_name, inner_fn())


class InternalFuncTest(unittest.TestCase):
    """Test :func:`autologging.logged` on an internal and inner internal
    function.

    """

    def test_internal_fn_logger(self):
        self.assertTrue(hasattr(_internal_fn, "__logger"))

    def test_internal_fn_logger_name(self):
        self.assertEqual("test.loggedfunctions._internal_fn",
                         getattr(_internal_fn, "__logger").name)

    def test_internal_inner_fn_logger(self):
        self.assertTrue(hasattr(_internal_fn(), "__logger"))

    def test_internal_inner_fn_logger_name(self):
        _inner_internal_fn = _internal_fn()
        if (hasattr(_inner_internal_fn, "__qualname__")):
            expected_name = \
                    "test.loggedfunctions._internal_fn.<locals>._inner_internal_fn"
        else:
            expected_name = "test.loggedfunctions._inner_internal_fn"
        self.assertEqual(expected_name,
                         getattr(_inner_internal_fn, "__logger").name)
        self.assertEqual(expected_name, _inner_internal_fn())


def suite():
    """Build the test suite for :func:`autologging.logged`."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModuleLoggerLoggedTest))
    suite.addTest(unittest.makeSuite(NamedLoggerLoggedTest))
    suite.addTest(unittest.makeSuite(OuterFuncTest))
    suite.addTest(unittest.makeSuite(InternalFuncTest))
    return suite


if (__name__ == "__main__"):
    unittest.TextTestRunner().run(suite())
