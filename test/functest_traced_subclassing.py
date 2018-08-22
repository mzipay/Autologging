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

"""Test case and runner for the :func:`autologging.traced` decorator
function.

This module specifically tests subclassing/inheritance behavior of
``@traced`` classes.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import TRACE, __version__
from test import dummy_module_logger, get_dummy_lineno, list_handler
from test.dummy import (
    _NonTracedParent,
    _TracedParent,
    NonTracedChildTracedParent,
    TracedChildNonTracedParent,
    TracedChildTracedParent,
)
from test.functest_traced import _TracedFunctionalTest

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


# healthy (?) paranoia ;)
def setUpModule():
    for class_ in [_TracedParent, _NonTracedParent]:
        for method in ["inherited_method", "overridden_method"]:
            assert method in class_.__dict__, \
                "%s.%s is not defined!" % (class_.__name__, method)

    for class_ in [
            NonTracedChildTracedParent, TracedChildNonTracedParent,
            TracedChildTracedParent]:
        assert "inherited_method" not in class_.__dict__, \
            "%s.inherited_method should not be defined here!" % class_.__name__
        assert "overridden_method" in class_.__dict__, \
            "%s.overridden_method is not defined!" % class_.__name__


class TracedSubclassingFunctionalTest(_TracedFunctionalTest):
    """Test the trace records emitted by classes when the parent class,
    the child class, or both, is decorated with
    :func:`autologging.traced`.

    """

    def setUp(self):
        dummy_module_logger.setLevel(TRACE)
        list_handler.reset()

    def test_nontraced_child_traced_parent_inherited_records(self):
        value = NonTracedChildTracedParent().inherited_method(None)
        self.assertEqual("_TP.i_m None and None", value)

        self.assertEqual(2, len(list_handler.records))

        traced_function = \
            _TracedParent.__dict__["inherited_method"].__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function,
            "test.dummy._TracedParent", ((None,), dict()), "_TP.i_m")
        self._assert_return_record(
            list_handler.records[1], traced_function,
            "test.dummy._TracedParent", ("_TP.i_m None and None",), "_TP.i_m")

    def test_nontraced_child_traced_parent_overridden_records(self):
        value = NonTracedChildTracedParent().overridden_method(None)
        self.assertEqual("_TP.o_m None and None NTCTP.o_m", value)

        self.assertEqual(2, len(list_handler.records))

        traced_function = \
            _TracedParent.__dict__["overridden_method"].__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function,
            "test.dummy._TracedParent", ((None,), dict(keyword=None)),
            "_TP.o_m")
        self._assert_return_record(
            list_handler.records[1], traced_function,
            "test.dummy._TracedParent", ("_TP.o_m None and None",), "_TP.o_m")

    def test_traced_child_nontraced_parent_inherited_records(self):
        value = TracedChildNonTracedParent().inherited_method(None)
        self.assertEqual("_NTP.i_m None and None", value)

        self.assertEqual(0, len(list_handler.records))

    def test_traced_child_nontraced_parent_overridden_records(self):
        value = TracedChildNonTracedParent().overridden_method(None)
        self.assertEqual("_NTP.o_m None and None TCNTP.o_m", value)

        self.assertEqual(2, len(list_handler.records))

        traced_function = \
            TracedChildNonTracedParent.__dict__[
                "overridden_method"].__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function,
            "test.dummy.TracedChildNonTracedParent",
            ((None,), dict()), "TCNTP.o_m")
        self._assert_return_record(
            list_handler.records[1], traced_function,
            "test.dummy.TracedChildNonTracedParent",
            ("_NTP.o_m None and None TCNTP.o_m",), "TCNTP.o_m")

    def test_traced_child_traced_parent_inherited_records(self):
        value = TracedChildTracedParent().inherited_method(None)
        self.assertEqual("_TP.i_m None and None", value)

        self.assertEqual(2, len(list_handler.records))

        traced_function = \
            _TracedParent.__dict__["inherited_method"].__wrapped__
        self._assert_call_record(
            list_handler.records[0], traced_function,
            "test.dummy._TracedParent", ((None,), dict()), "_TP.i_m")
        self._assert_return_record(
            list_handler.records[1], traced_function,
            "test.dummy._TracedParent", ("_TP.i_m None and None",), "_TP.i_m")

    def test_traced_child_traced_parent_overridden_records(self):
        value = TracedChildTracedParent().overridden_method(None)
        self.assertEqual("_TP.o_m None and None TCTP.o_m", value)

        # child CALL, parent CALL, parent RETURN, child RETURN
        self.assertEqual(4, len(list_handler.records))

        child_call, parent_call, parent_return, child_return = \
            list_handler.records
        child_function = \
            TracedChildTracedParent.__dict__["overridden_method"].__wrapped__
        parent_function = \
            _TracedParent.__dict__["overridden_method"].__wrapped__
        self._assert_call_record(
            child_call, child_function, "test.dummy.TracedChildTracedParent",
            ((None,), dict()), "TCTP.o_m")
        self._assert_call_record(
            parent_call, parent_function, "test.dummy._TracedParent",
            ((None,), dict(keyword=None)), "_TP.o_m")
        self._assert_return_record(
            parent_return, parent_function, "test.dummy._TracedParent",
            ("_TP.o_m None and None",), "_TP.o_m")
        self._assert_return_record(
            child_return, child_function, "test.dummy.TracedChildTracedParent",
            ("_TP.o_m None and None TCTP.o_m",), "TCTP.o_m")


def suite():
    return unittest.makeSuite(TracedSubclassingFunctionalTest)


if (__name__ == "__main__"):
    unittest.TextTestRunner().run(suite())

