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

"""Test case and runner for :func:`autologging._is_internal_name`."""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import unittest

from autologging import _is_internal_name, __version__


class IsInternalNameTest(unittest.TestCase):
    """Test the :func:`autologging._is_internal_name` function."""

    def test_does_not_match_public_method_name(self):
        self.assertFalse(_is_internal_name("public"))

    def test_does_not_match_nonpublic_method_name(self):
        self.assertFalse(_is_internal_name("_nonpublic"))

    def test_does_not_match_mangled_method_name(self):
        self.assertFalse(_is_internal_name("_ClassName__internal"))

    def test_does_not_match_special_method_name(self):
        self.assertFalse(_is_internal_name("__special__"))

    def test_matches_internal_method_name(self):
        self.assertTrue(_is_internal_name("__internal"))


def suite():
    return unittest.makeSuite(IsInternalNameTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

