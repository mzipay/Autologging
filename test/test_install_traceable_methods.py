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
:func:`autologging._install_traceable_methods`.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import unittest
import warnings

from autologging import _install_traceable_methods, __version__

from test import named_logger


class SampleClass(object):

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

    def _nonpublic(self):
        pass

    def __internal(self):
        pass

    def __special__(self):
        pass


_original_method_descriptors = dict(
    [(method_name, SampleClass.__dict__[method_name]) for method_name in [
        "class_method",
        "static_method",
        "__init__",
        "public",
        "_nonpublic",
        "_SampleClass__internal",
        "__special__",
    ]])


class InstallTraceableMethodsTest(unittest.TestCase):
    """Test the :func:`autologging._install_traceable_methods`
    function.

    """

    def tearDown(self):
        for method_name in [
                "class_method",
                "static_method"]:
            setattr(
                SampleClass, method_name,
                _original_method_descriptors[method_name])

        for method_name in [
                "__init__",
                "public",
                "_nonpublic",
                "_SampleClass__internal",
                "__special__"]:
            setattr(
                SampleClass, method_name,
                _original_method_descriptors[method_name])

    def test_does_not_replace_class(self):
        class_ = _install_traceable_methods(SampleClass)

        self.assertTrue(class_ is SampleClass)

    def test_traces_default_methods_if_none_are_named(self):
        _install_traceable_methods(SampleClass)

        for traced_method_name in [
                "class_method",
                "static_method"]:
            descriptor = SampleClass.__dict__[traced_method_name]
            self.assertTrue(
                hasattr(descriptor.__func__, "__autologging_traced__"),
                traced_method_name)

        for traced_method_name in [
                "__init__",
                "public",
                "_nonpublic",
                "_SampleClass__internal"]:
            descriptor = SampleClass.__dict__[traced_method_name]
            self.assertTrue(
                hasattr(descriptor, "__autologging_traced__"),
                traced_method_name)

        self.assertFalse(
            hasattr(
                SampleClass.__dict__["__special__"], "__autologging_traced__"),
            "__special__")

    def test_traces_named_methods_only(self):
        _install_traceable_methods(SampleClass, "public", "__special__")

        for nontraced_method_name in [
                "class_method",
                "static_method"]:
            descriptor = SampleClass.__dict__[nontraced_method_name]
            self.assertFalse(
                hasattr(descriptor.__func__, "__autologging_traced__"),
                nontraced_method_name)

        for nontraced_method_name in [
                "__init__",
                "_nonpublic",
                "_SampleClass__internal"]:
            descriptor = SampleClass.__dict__[nontraced_method_name]
            self.assertFalse(
                hasattr(descriptor, "__autologging_traced__"),
                nontraced_method_name)

        for traced_method_name in [
                "public",
                "__special__"]:
            descriptor = SampleClass.__dict__[traced_method_name]
            self.assertTrue(
                hasattr(descriptor, "__autologging_traced__"),
                traced_method_name)

    def test_traces_with_default_logger(self):
        _install_traceable_methods(SampleClass)

        for traced_method_name in [
                "class_method",
                "static_method"]:
            descriptor = SampleClass.__dict__[traced_method_name]
            self.assertEqual(
                "%s.SampleClass" % __name__,
                descriptor.__func__._tracing_proxy.logger.name)

        for traced_method_name in [
                "__init__",
                "public",
                "_nonpublic",
                "_SampleClass__internal"]:
            descriptor = SampleClass.__dict__[traced_method_name]
            self.assertEqual(
                "%s.SampleClass" % __name__,
                descriptor._tracing_proxy.logger.name)

    def test_traces_with_named_logger(self):
        _install_traceable_methods(SampleClass, logger=named_logger)

        for traced_method_name in [
                "class_method",
                "static_method"]:
            descriptor = SampleClass.__dict__[traced_method_name]
            self.assertEqual(
                named_logger.name,
                descriptor.__func__._tracing_proxy.logger.name)

        for traced_method_name in [
                "__init__",
                "public",
                "_nonpublic",
                "_SampleClass__internal"]:
            descriptor = SampleClass.__dict__[traced_method_name]
            self.assertEqual(
                named_logger.name,
                descriptor._tracing_proxy.logger.name)


def suite():
    return unittest.makeSuite(InstallTraceableMethodsTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

