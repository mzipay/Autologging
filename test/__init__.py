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

"""Utilities for Autologging unit and functional tests."""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

from functools import partial
import logging
import os
import unittest

from autologging import TRACE, __version__

__all__ = [
    "dummy_module_logger",
    "get_lineno",
    "get_dummy_lineno",
    "has_co_lnotab",
    "list_handler",
    "named_logger",
    "named_tracer",
    "suite",
]


def get_lineno(filename, marker):
    fn = os.path.join(
        os.path.dirname(get_lineno.__code__.co_filename),
        os.path.basename(filename))
    with open(fn) as fp:
        for (i, line) in enumerate(fp):
            if marker in line:
                return i + 1


def get_dummy_lineno(marker):
    return get_lineno("dummy.py", marker)


has_co_lnotab = hasattr(get_dummy_lineno.__code__, "co_lnotab")


class _ListHandler(logging.Handler):
    """Store log records in the order in which they are emitted."""

    def __init__(self, *args, **keywords):
        super(_ListHandler, self).__init__(*args, **keywords)
        self.reset()

    records = property(lambda self: self._records)
    
    def emit(self, record):
        self._records.append(record)

    
    def reset(self):
        self._records = []


list_handler = _ListHandler(level=TRACE)

dummy_module_logger = logging.getLogger("test.dummy")
dummy_module_logger.addHandler(list_handler)

named_logger = logging.getLogger("logged.testing")
named_logger.addHandler(list_handler)

named_tracer = logging.getLogger("traced.testing")
named_tracer.addHandler(list_handler)


def suite():
    from test import (
        test_logged,
        test_traced,
        test_traced_noop,
        test_install_traced_noop,
        test_install_traced_noop_envauto,
        test_generate_logger_name,
        test_add_logger_to,
        test_make_traceable_function,
        test_install_traceable_methods,
        test_get_traceable_method_names,
        test_get_default_traceable_method_names,
        test_is_internal_name,
        test_mangle_name,
        test_is_special_name,
        test_make_traceable_instancemethod,
        test_make_traceable_classmethod,
        test_make_traceable_staticmethod,
        test_find_lastlineno,
        test_FunctionTracingProxy,
        test_GeneratorIteratorTracingProxy,
        functest_logged,
        functest_traced,
        functest_traced_subclassing,
        functest_logged_and_traced,
        functest_traced_generator,
    )

    suite = unittest.TestSuite()

    suite.addTest(test_logged.suite())
    suite.addTest(test_traced.suite())
    suite.addTest(test_traced_noop.suite())
    suite.addTest(test_install_traced_noop.suite())
    suite.addTest(test_install_traced_noop_envauto.suite())
    suite.addTest(test_generate_logger_name.suite())
    suite.addTest(test_add_logger_to.suite())
    suite.addTest(test_make_traceable_function.suite())
    suite.addTest(test_install_traceable_methods.suite())
    suite.addTest(test_get_traceable_method_names.suite())
    suite.addTest(test_get_default_traceable_method_names.suite())
    suite.addTest(test_is_internal_name.suite())
    suite.addTest(test_mangle_name.suite())
    suite.addTest(test_is_special_name.suite())
    suite.addTest(test_make_traceable_instancemethod.suite())
    suite.addTest(test_make_traceable_classmethod.suite())
    suite.addTest(test_make_traceable_staticmethod.suite())
    suite.addTest(test_find_lastlineno.suite())
    suite.addTest(test_FunctionTracingProxy.suite())
    suite.addTest(test_GeneratorIteratorTracingProxy.suite())
    suite.addTest(functest_logged.suite())
    suite.addTest(functest_traced.suite())
    suite.addTest(functest_traced_subclassing.suite())
    suite.addTest(functest_logged_and_traced.suite())
    suite.addTest(functest_traced_generator.suite())

    return suite

