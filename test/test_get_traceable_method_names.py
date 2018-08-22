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

"""Test case and runner for
:func:`autologging._get_traceable_method_names`.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import unittest
import warnings

from autologging import _get_traceable_method_names, __version__


class Parent(object):

    def inherited(self):
        pass

    def overridden(self):
        pass


class SampleClass(Parent):

    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass

    def __init__(self):
        pass

    def public(self):
        pass

    def overridden(self):
        pass

    def _nonpublic(self):
        pass

    def __internal(self):
        pass

    def __eq__(self, other):
        return False


class GetTraceableMethodNamesTest(unittest.TestCase):
    """Test the :func:`autologging._get_traceable_method_names`
    function.

    """

    def test_mangles_internal_names(self):
        actual_method_names = _get_traceable_method_names([
            "__internal"], SampleClass)
        self.assertEqual([
            "_SampleClass__internal"], actual_method_names)

    def test_identifies_named_methods_defined_in_class(self):
        actual_method_names = _get_traceable_method_names(
            [
                "class_method",
                "static_method",
                "__init__",
                "public",
                "overridden",
                "_nonpublic",
                "__internal",
                "__eq__"
            ],
            SampleClass)

        self.assertEqual(
            sorted([
                "class_method",
                "static_method",
                "__init__",
                "public",
                "overridden",
                "_nonpublic",
                "_SampleClass__internal",
                "__eq__",
            ]),
            sorted(actual_method_names))

    def test_issues_warning_for_missing_method(self):
        with warnings.catch_warnings(record = True) as w:
            warnings.simplefilter("always")
            _get_traceable_method_names(["inherited"], SampleClass)
            self.assertEqual(1, len(w))
            self.assertEqual(
                "'inherited' does not identify a method defined in SampleClass",
                str(w[0].message))


def suite():
    return unittest.makeSuite(GetTraceableMethodNamesTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

