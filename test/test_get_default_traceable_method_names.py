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
:func:`autologging._get_default_traceable_method_names`.

"""
__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import unittest

from autologging import _get_default_traceable_method_names, __version__


class Parent(object):

    def inherited(self):
        pass

    def overridden(self):
        pass

    def __call__(self):
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


class GetDefaultTraceableMethodNamesTest(unittest.TestCase):
    """Test the :func:`autologging._get_default_traceable_method_names`
    function.

    """

    def setUp(self):
        self.method_names = _get_default_traceable_method_names(SampleClass)

    def test_identifies_classmethod(self):
        self.assertTrue("class_method" in self.method_names)

    def test_identifies_staticmethod(self):
        self.assertTrue("static_method" in self.method_names)

    def test_identifies_init_method(self):
        self.assertTrue("__init__" in self.method_names)

    def test_identifies_public_method(self):
        self.assertTrue("public" in self.method_names)

    def test_identifies_overridden_method(self):
        self.assertTrue("overridden" in self.method_names)

    def test_identifies_nonpublic_method(self):
        self.assertTrue("_nonpublic" in self.method_names)

    def test_identifies_internal_method(self):
        self.assertTrue("_SampleClass__internal" in self.method_names)

    def test_does_not_identify_inherited_method(self):
        self.assertFalse("inherited" in self.method_names)

    def test_does_not_identify_special_method(self):
        self.assertFalse("__eq__" in self.method_names)

    def test_identifies_call_magic_method(self):
        self.assertTrue(
                "__call__" in _get_default_traceable_method_names(Parent))

    def test_does_not_identify_inherited_call_magic_method(self):
        self.assertFalse("__call__" in self.method_names)


def suite():
    return unittest.makeSuite(GetDefaultTraceableMethodNamesTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

