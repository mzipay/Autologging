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

"""Functional test cases and runner for the :func:`autologging.logged`
decorator function.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import __version__, _is_ironpython

from test import (
    dummy_module_logger,
    get_dummy_lineno,
    list_handler,
    named_logger,
)
from test.dummy import LoggedClass, logged_function

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class _LoggedFunctionalTest(unittest.TestCase):

    def setUp(self):
        dummy_module_logger.setLevel(logging.INFO)
        named_logger.setLevel(logging.INFO)
        list_handler.reset()

    def _assert_log_record(
            self, info_record, logged_function, expected_logger_name, marker):
        expected_message = "%s message" % marker
        self.assertEqual(expected_logger_name, info_record.name)
        self.assertEqual(expected_message, info_record.msg)
        self.assertEqual(tuple(), info_record.args)
        self.assertEqual("INFO", info_record.levelname)
        self.assertEqual(logging.INFO, info_record.levelno)
        # IronPython doesn't handle frames or code objects fully (even with
        # -X:FullFrames)
        if not _is_ironpython:
            self.assertEqual(
                logged_function.__code__.co_filename, info_record.pathname)
            self.assertEqual(
                get_dummy_lineno(expected_message), info_record.lineno)
            self.assertEqual(logged_function.__name__, info_record.funcName)


class LoggedClassFunctionalTest(_LoggedFunctionalTest):
    """Test the log records emitted by an :func:`autologging.logged`
    decorated class.

    """

    def test_staticmethod_log_record(self):
        LoggedClass.static_method()

        self.assertEqual(1, len(list_handler.records))
        self._assert_log_record(
            list_handler.records[0],
            LoggedClass.__dict__["static_method"].__func__,
            "test.dummy.LoggedClass", "LC.s_m")

    def test_classmethod_log_record(self):
        LoggedClass.class_method()

        self.assertEqual(1, len(list_handler.records))
        self._assert_log_record(
            list_handler.records[0],
            LoggedClass.__dict__["class_method"].__func__,
            "test.dummy.LoggedClass", "LC.c_m")

    def test_instance_method_log_record(self):
        LoggedClass()

        self.assertEqual(1, len(list_handler.records))
        self._assert_log_record(
            list_handler.records[0], LoggedClass.__dict__["__init__"],
            "test.dummy.LoggedClass", "LC.__i__")

    def test_nested_class_log_record(self):
        LoggedClass.NestedClass()

        self.assertEqual(1, len(list_handler.records))

        expected_logger_name = "test.dummy.%s" % getattr(
            LoggedClass.NestedClass, "__qualname__", "NestedClass")
        self._assert_log_record(
            list_handler.records[0],
            LoggedClass.NestedClass.__dict__["__init__"], expected_logger_name,
            "LC.NC.__i__")

    def test_internal_nested_class_log_record(self):
        LoggedClass._LoggedClass__InternalNestedClass()

        self.assertEqual(1, len(list_handler.records))

        expected_logger_name = "logged.testing.%s" % getattr(
            LoggedClass._LoggedClass__InternalNestedClass, "__qualname__",
            LoggedClass._LoggedClass__InternalNestedClass.__name__)
        self._assert_log_record(
            list_handler.records[0],
            LoggedClass._LoggedClass__InternalNestedClass.__dict__["__init__"],
            expected_logger_name, "LC.__INC.__i__")


class LoggedFunctionFunctionalTest(_LoggedFunctionalTest):
    """Test the log records emitted by an :func:`autologging.logged`
    decorated function.

    """

    def test_function_log_record(self):
        logged_function()

        self.assertEqual(1, len(list_handler.records))
        self._assert_log_record(
            list_handler.records[0], logged_function, "test.dummy", "l_f")

    def test_nested_function_log_record(self):
        nested_function = logged_function()
        nested_function()

        self.assertEqual(2, len(list_handler.records))
        self._assert_log_record(
            list_handler.records[1], nested_function, "logged.testing",
            "l_f.n_f")


def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(LoggedClassFunctionalTest))
    suite.addTest(unittest.makeSuite(LoggedFunctionFunctionalTest))

    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

