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

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.2"

import logging
import os
import unittest

from test import ListHandler
from test.loggedclasses import (ModuleLoggerClass, NamedLoggerClass,
                                OuterClass, _InternalClass)

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class ModuleLoggerLoggedTest(unittest.TestCase):
    """Test :func:`autologging.logged` using the default (module) logger."""

    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger("test.loggedclasses.ModuleLoggerClass")
        logger.setLevel(logging.DEBUG)
        cls._handler = ListHandler(level=logging.DEBUG)
        logger.addHandler(cls._handler)
        cls.expected_name = "test.loggedclasses.ModuleLoggerClass"
        cls.expected_levelname = "INFO"
        cls.expected_levelno = logging.INFO
        cls.expected_pathname = \
            ModuleLoggerClass.logged_instancemethod.__code__.co_filename  # @UndefinedVariable
        cls.expected_filename = os.path.basename(cls.expected_pathname)
        cls.expected_module = os.path.splitext(cls.expected_filename)[0]

    def test_staticmethod_call(self):
        ModuleLoggerClass.logged_staticmethod()
        record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, record.name)
        self.assertEqual(self.expected_levelname, record.levelname)
        self.assertEqual(self.expected_levelno, record.levelno)
        self.assertEqual(self.expected_pathname, record.pathname)
        self.assertEqual(self.expected_filename, record.filename)
        self.assertEqual(self.expected_module, record.module)
        self.assertEqual(44, record.lineno)
        self.assertEqual("logged_staticmethod", record.funcName)
        self.assertEqual("ModuleLoggerClass.logged_staticmethod test.",
                         record.getMessage())

    def test_classmethod_call(self):
        ModuleLoggerClass.logged_classmethod()
        record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, record.name)
        self.assertEqual(self.expected_levelname, record.levelname)
        self.assertEqual(self.expected_levelno, record.levelno)
        self.assertEqual(self.expected_pathname, record.pathname)
        self.assertEqual(self.expected_filename, record.filename)
        self.assertEqual(self.expected_module, record.module)
        self.assertEqual(49, record.lineno)
        self.assertEqual("logged_classmethod", record.funcName)
        self.assertEqual("ModuleLoggerClass.logged_classmethod test.",
                         record.getMessage())

    def test_instancemethod_call(self):
        instance = ModuleLoggerClass()
        instance.logged_instancemethod()
        record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, record.name)
        self.assertEqual(self.expected_levelname, record.levelname)
        self.assertEqual(self.expected_levelno, record.levelno)
        self.assertEqual(self.expected_pathname, record.pathname)
        self.assertEqual(self.expected_filename, record.filename)
        self.assertEqual(self.expected_module, record.module)
        self.assertEqual(53, record.lineno)
        self.assertEqual("logged_instancemethod", record.funcName)
        self.assertEqual("ModuleLoggerClass.logged_instancemethod test.",
                         record.getMessage())


class NamedLoggerLoggedTest(unittest.TestCase):
    """Test :func:`autologging.logged` using a user-named logger."""

    @classmethod
    def setUpClass(cls):
        logger = logging.getLogger("logged.testing.NamedLoggerClass")
        logger.setLevel(logging.DEBUG)
        cls._handler = ListHandler(level=logging.DEBUG)
        logger.addHandler(cls._handler)
        cls.expected_name = "logged.testing.NamedLoggerClass"
        cls.expected_levelname = "INFO"
        cls.expected_levelno = logging.INFO
        cls.expected_pathname = \
            NamedLoggerClass.logged_instancemethod.__code__.co_filename  # @UndefinedVariable
        cls.expected_filename = os.path.basename(cls.expected_pathname)
        cls.expected_module = os.path.splitext(cls.expected_filename)[0]

    def test_staticmethod_call(self):
        NamedLoggerClass.logged_staticmethod()
        record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, record.name)
        self.assertEqual(self.expected_levelname, record.levelname)
        self.assertEqual(self.expected_levelno, record.levelno)
        self.assertEqual(self.expected_pathname, record.pathname)
        self.assertEqual(self.expected_filename, record.filename)
        self.assertEqual(self.expected_module, record.module)
        self.assertEqual(67, record.lineno)
        self.assertEqual("logged_staticmethod", record.funcName)
        self.assertEqual("NamedLoggerClass.logged_staticmethod test.",
                         record.getMessage())

    def test_classmethod_call(self):
        NamedLoggerClass.logged_classmethod()
        record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, record.name)
        self.assertEqual(self.expected_levelname, record.levelname)
        self.assertEqual(self.expected_levelno, record.levelno)
        self.assertEqual(self.expected_pathname, record.pathname)
        self.assertEqual(self.expected_filename, record.filename)
        self.assertEqual(self.expected_module, record.module)
        self.assertEqual(72, record.lineno)
        self.assertEqual("logged_classmethod", record.funcName)
        self.assertEqual("NamedLoggerClass.logged_classmethod test.",
                         record.getMessage())

    def test_instancemethod_call(self):
        instance = NamedLoggerClass()
        instance.logged_instancemethod()
        record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, record.name)
        self.assertEqual(self.expected_levelname, record.levelname)
        self.assertEqual(self.expected_levelno, record.levelno)
        self.assertEqual(self.expected_pathname, record.pathname)
        self.assertEqual(self.expected_filename, record.filename)
        self.assertEqual(self.expected_module, record.module)
        self.assertEqual(76, record.lineno)
        self.assertEqual("logged_instancemethod", record.funcName)
        self.assertEqual("NamedLoggerClass.logged_instancemethod test.",
                         record.getMessage())


class OuterClassTest(unittest.TestCase):
    """Test :func:`autologging.logged` on an inner class."""

    def test_inner_class_logger_name(self):
        if (hasattr(OuterClass.InnerClass, "__qualname__")):
            expected_name = "test.loggedclasses.OuterClass.InnerClass"
        else:
            expected_name = "test.loggedclasses.InnerClass"
        self.assertEqual(expected_name,
                         OuterClass.InnerClass._InnerClass__logger.name)


class InternalClassTest(unittest.TestCase):
    """Test :func:`autologging.logged` on an internal and inner internal
    class.

    """

    def test_internal_class_logger_member(self):
        self.assertTrue(hasattr(_InternalClass, "_InternalClass__logger"))

    def test_internal_class_logger_name(self):
        self.assertEqual("test.loggedclasses._InternalClass",
                         _InternalClass._InternalClass__logger.name)

    def test_internal_inner_class_logger_member(self):
        self.assertTrue(hasattr(_InternalClass._InnerInternalClass,
                                "_InnerInternalClass__logger"))

    def test_internal_inner_class_logger_name(self):
        if (hasattr(_InternalClass._InnerInternalClass, "__qualname__")):
            expected_name = \
                    "test.loggedclasses._InternalClass._InnerInternalClass"
        else:
            expected_name = "test.loggedclasses._InnerInternalClass"
        self.assertEqual(
            expected_name,
            _InternalClass._InnerInternalClass._InnerInternalClass__logger.name)


def suite():
    """Build the test suite for :func:`autologging.logged`."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModuleLoggerLoggedTest))
    suite.addTest(unittest.makeSuite(NamedLoggerLoggedTest))
    suite.addTest(unittest.makeSuite(OuterClassTest))
    suite.addTest(unittest.makeSuite(InternalClassTest))
    return suite


if (__name__ == "__main__"):
    unittest.TextTestRunner().run(suite())
