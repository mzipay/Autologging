# -*- coding: utf-8 -*-

# Copyright (c) 2013-2015 Matthew Zipay <mattz@ninthtest.net>
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

__author__ = "Matthew Zipay <mattz@ninthtest.net>, "\
             "Simon Knopp <simon.knopp@pg.canterbury.ac.nz>"
__version__ = "0.4.0"

import logging
import os
import unittest

from test import dummy_module_logger, list_handler
from test.dummy import LoggedClass, logged_function

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class LoggedDecoratorTest(unittest.TestCase):
    """Test :func:`autologging.logged`."""

    @classmethod
    def setUpClass(cls):
        dummy_module_logger.setLevel(logging.INFO)

    def setUp(self):
        list_handler.reset()

    def test_logged_sets_correct_class_logger(self):
        self.assertEqual("test.dummy.LoggedClass",
                         LoggedClass._LoggedClass__logger.name)
        self.assertEqual("logged.testing.LoggedClass.NestedClass"
                            if _has_qualname else "logged.testing.NestedClass",
                         LoggedClass.NestedClass._NestedClass__logger.name)
        self.assertEqual("test.dummy.LoggedClass._NonPublicNestedClass"
                            if _has_qualname else
                            "test.dummy._NonPublicNestedClass",
                         LoggedClass._NonPublicNestedClass.
                            _NonPublicNestedClass__logger.name)
        self.assertEqual("test.dummy.LoggedClass.__MangledNestedClass"
                            if _has_qualname else
                            "test.dummy.__MangledNestedClass",
                         LoggedClass._LoggedClass__MangledNestedClass.
                            _MangledNestedClass__logger.name)

    def test_staticmethod_log_record_is_accurate(self):
        LoggedClass.static_method()
        self.assertEqual(1, len(list_handler.records))
        record = list_handler.records.pop()
        self.assertEqual("test.dummy.LoggedClass", record.name)

    def test_classmethod_log_record_is_accurate(self):
        LoggedClass.class_method()
        self.assertEqual(1, len(list_handler.records))
        record = list_handler.records.pop()
        self.assertEqual("test.dummy.LoggedClass", record.name)

    def test_instance_method_log_record_is_accurate(self):
        LoggedClass().instance_method()
        self.assertEqual(1, len(list_handler.records))
        record = list_handler.records.pop()
        self.assertEqual("test.dummy.LoggedClass", record.name)

    def test_special_method_log_record_is_accurate(self):
        LoggedClass() == object()
        self.assertEqual(1, len(list_handler.records))
        record = list_handler.records.pop()
        self.assertEqual("test.dummy.LoggedClass", record.name)

    def test_nested_class_log_record_is_accurate(self):
        LoggedClass.NestedClass()
        self.assertEqual(1, len(list_handler.records))
        record = list_handler.records.pop()
        self.assertEqual("logged.testing.LoggedClass.NestedClass"
                            if _has_qualname else "logged.testing.NestedClass",
                         record.name)

    def test_nonpublic_nested_class_log_record_is_accurate(self):
        LoggedClass._NonPublicNestedClass()
        self.assertEqual(1, len(list_handler.records))
        record = list_handler.records.pop()
        self.assertEqual("test.dummy.LoggedClass._NonPublicNestedClass"
                            if _has_qualname else
                            "test.dummy._NonPublicNestedClass",
                         record.name)

    def test_mangled_nested_class_log_record_is_accurate(self):
        LoggedClass._LoggedClass__MangledNestedClass()
        self.assertEqual(1, len(list_handler.records))
        record = list_handler.records.pop()
        self.assertEqual("test.dummy.LoggedClass.__MangledNestedClass"
                            if _has_qualname else
                            "test.dummy.__MangledNestedClass",
                         record.name)

    def test_logged_sets_correct_function_logger(self):
        self.assertEqual("test.dummy", logged_function._logger.name)
        self.assertEqual("logged.testing", logged_function()._logger.name)

    def test_function_log_record_is_accurate(self):
        logged_function()
        self.assertEqual(1, len(list_handler.records))
        record = list_handler.records.pop()
        self.assertEqual("test.dummy", record.name)

    def test_nested_function_log_record_is_accurate(self):
        nested_function = logged_function()
        list_handler.reset()
        nested_function()
        self.assertEqual(1, len(list_handler.records))
        record = list_handler.records.pop()
        self.assertEqual("logged.testing", record.name)


_has_qualname = hasattr(LoggedDecoratorTest, "__qualname__")


def suite():
    """Build the test suite for :func:`autologging.logged`."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LoggedDecoratorTest))

    return suite


if (__name__ == "__main__"):
    unittest.TextTestRunner().run(suite())

