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

"""Test cases and runner for the :func:`autologging.traced` decorator
function.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.1"

import logging
import os
import sys
import unittest

from autologging import TRACE
from test import ListHandler
from test.tracedfunctions import module_logger_function, named_logger_function

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class ModuleLoggerTracedTest(unittest.TestCase):
    """Test :func:`autologging.traced` using the default (module) logger."""

    @classmethod
    def setUpClass(cls):
        # the testing handler needs to be added to the logger proxy, which is
        # a free variable of the module_logger_function tracer closure
        closure_index = \
            module_logger_function.__code__.co_freevars.index("logger_proxy")  # @UndefinedVariable
        logger_proxy = \
            module_logger_function.__closure__[closure_index].cell_contents
        logger_proxy.setLevel(TRACE)
        cls._handler = ListHandler(level=TRACE)
        logger_proxy.addHandler(cls._handler)
        cls.expected_name = "test.tracedfunctions"
        cls.expected_levelname = "TRACE"
        cls.expected_levelno = TRACE
        # the expected pathname needs to be fetched from the original
        # module_logger_function (not the tracer proxy function); the original
        # is available as a free variable of the module_logger_function tracer
        # closure
        closure_index = \
            module_logger_function.__code__.co_freevars.index("function")  # @UndefinedVariable
        function = \
            module_logger_function.__closure__[closure_index].cell_contents
        cls.expected_pathname = function.__code__.co_filename
        cls.expected_filename = os.path.basename(cls.expected_pathname)
        cls.expected_module = os.path.splitext(cls.expected_filename)[0]

    def test_traced_call(self):
        value = module_logger_function("spam", keyword="eggs")
        self.assertEqual("spam and eggs", value)
        return_record = self._handler.records.pop()
        call_record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, call_record.name)
        self.assertEqual(self.expected_levelname, call_record.levelname)
        self.assertEqual(self.expected_levelno, call_record.levelno)
        self.assertEqual(self.expected_pathname, call_record.pathname)
        self.assertEqual(self.expected_filename, call_record.filename)
        self.assertEqual(self.expected_module, call_record.module)
        self.assertEqual(36, call_record.lineno)
        self.assertEqual("module_logger_function", call_record.funcName)
        self.assertEqual(
            "CALL module_logger_function *('spam',) **{'keyword': 'eggs'}",
            call_record.getMessage())
        self.assertEqual(self.expected_name, return_record.name)
        self.assertEqual(self.expected_levelname, return_record.levelname)
        self.assertEqual(self.expected_levelno, return_record.levelno)
        self.assertEqual(self.expected_pathname, return_record.pathname)
        self.assertEqual(self.expected_filename, return_record.filename)
        self.assertEqual(self.expected_module, return_record.module)
        self.assertEqual(39, return_record.lineno)
        self.assertEqual("module_logger_function", return_record.funcName)
        self.assertEqual("RETURN module_logger_function 'spam and eggs'",
                         return_record.getMessage())

    def test_traced_magicattrs(self):
        self.assertEqual("test.tracedfunctions",
                         module_logger_function.__module__,  # @UndefinedVariable
                         "module_logger_function.__module__")
        self.assertEqual("module_logger_function",
                         module_logger_function.__name__,  # @UndefinedVariable
                         "module_logger_function.__name__")
        self.assertEqual("Function traced with module logger.",
                         module_logger_function.__doc__,
                         "module_logger_function.__doc__")
        if (sys.version_info.major >= 3):
            self.assertEqual(dict(), module_logger_function.__annotations__,  # @UndefinedVariable
                             "module_logger_function.__annotations__")
            if (sys.version_info.minor >= 3):
                self.assertEqual("module_logger_function",
                                 module_logger_function.__qualname__,  # @UndefinedVariable
                                 "module_logger_function.__qualname__")


class NamedLoggerTracedTest(unittest.TestCase):
    """Test :func:`autologging.traced` using a user-named logger."""

    @classmethod
    def setUpClass(cls):
        # the testing handler needs to be added to the logger proxy, which is
        # a free variable of the named_logger_function tracer closure
        closure_index = \
            named_logger_function.__code__.co_freevars.index("logger_proxy")  # @UndefinedVariable
        logger_proxy = \
            named_logger_function.__closure__[closure_index].cell_contents
        logger_proxy.setLevel(TRACE)
        cls._handler = ListHandler(level=TRACE)
        logger_proxy.addHandler(cls._handler)
        cls.expected_name = "traced.testing"
        cls.expected_levelname = "TRACE"
        cls.expected_levelno = TRACE
        # the expected pathname needs to be fetched from the original
        # named_logger_function (not the tracer proxy function); the original
        # is available as a free variable of the named_logger_function tracer
        # closure
        closure_index = \
            named_logger_function.__code__.co_freevars.index("function")  # @UndefinedVariable
        function = \
            named_logger_function.__closure__[closure_index].cell_contents
        cls.expected_pathname = function.__code__.co_filename
        cls.expected_filename = os.path.basename(cls.expected_pathname)
        cls.expected_module = os.path.splitext(cls.expected_filename)[0]

    def test_traced_call(self):
        value = named_logger_function("green eggs", keyword="ham")
        self.assertEqual("green eggs and ham", value)
        return_record = self._handler.records.pop()
        call_record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, call_record.name)
        self.assertEqual(self.expected_levelname, call_record.levelname)
        self.assertEqual(self.expected_levelno, call_record.levelno)
        self.assertEqual(self.expected_pathname, call_record.pathname)
        self.assertEqual(self.expected_filename, call_record.filename)
        self.assertEqual(self.expected_module, call_record.module)
        self.assertEqual(45, call_record.lineno)
        self.assertEqual("named_logger_function", call_record.funcName)
        self.assertEqual(
            "CALL named_logger_function *('green eggs',) **{'keyword': 'ham'}",
            call_record.getMessage())
        self.assertEqual(self.expected_name, return_record.name)
        self.assertEqual(self.expected_levelname, return_record.levelname)
        self.assertEqual(self.expected_levelno, return_record.levelno)
        self.assertEqual(self.expected_pathname, return_record.pathname)
        self.assertEqual(self.expected_filename, return_record.filename)
        self.assertEqual(self.expected_module, return_record.module)
        self.assertEqual(48, return_record.lineno)
        self.assertEqual("named_logger_function", return_record.funcName)
        self.assertEqual("RETURN named_logger_function 'green eggs and ham'",
                         return_record.getMessage())

    def test_traced_magicattrs(self):
        self.assertEqual("test.tracedfunctions",
                         named_logger_function.__module__,  # @UndefinedVariable
                         "named_logger_function.__module__")
        self.assertEqual("named_logger_function",
                         named_logger_function.__name__,  # @UndefinedVariable
                         "named_logger_function.__name__")
        self.assertEqual("Function traced with named logger.",
                         named_logger_function.__doc__,
                         "named_logger_function.__doc__")
        if (sys.version_info.major >= 3):
            self.assertEqual(dict(), named_logger_function.__annotations__,  # @UndefinedVariable
                             "named_logger_function.__annotations__")
            if (sys.version_info.minor >= 3):
                self.assertEqual("module_logger_function",
                                 module_logger_function.__qualname__,  # @UndefinedVariable
                                 "module_logger_function.__qualname__")


def suite():
    """Build the test suite for :func:`autologging.traced`."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModuleLoggerTracedTest))
    suite.addTest(unittest.makeSuite(NamedLoggerTracedTest))
    return suite


if (__name__ == "__main__"):
    unittest.TextTestRunner().run(suite())
