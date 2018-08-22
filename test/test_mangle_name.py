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

"""Test case and runner for :func:`autologging._mangle_name`."""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import unittest

from autologging import _mangle_name, __version__


class MangleNameTest(unittest.TestCase):
    """Test the :func:`autologging._mangle_name` function."""

    def test_mangles_name_for_public_class(self):
        self.assertEqual(
            "_PublicClass__name", _mangle_name("__name", "PublicClass"))

    def test_mangles_name_for_nonpublic_class(self):
        self.assertEqual(
            "_NonPublicClass__name", _mangle_name("__name", "_NonPublicClass"))

    def test_mangles_name_for_internal_class(self):
        self.assertEqual(
            "_InternalClass__name", _mangle_name("__name", "__InternalClass"))


def suite():
    return unittest.makeSuite(MangleNameTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

