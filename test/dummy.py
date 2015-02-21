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

"""Dummy classes and functions used by :mod:`test.test_logged` to test
the :func:`autologging.logged` decorator.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>, "\
             "Simon Knopp <simon.knopp@pg.canterbury.ac.nz>"
__version__ = "0.4.0"

import sys

from autologging import logged, traced

from test import named_logger, named_tracer

__all__ = [
    "_TracedParent",
    "dummyM_module_logger",
    "get_dummyM_lineno",
    "logged_and_traced_function",
    "logged_function",
    "LoggedAndTracedClass",
    "LoggedClass",
    "NonTracedChildTracedParent",
    "traced_function",
    "TracedChildNonTracedParent",
    "TracedChildTracedParent",
]

_is_py3 = (sys.version_info[0] == 3)


@logged
class LoggedClass(object):
    """Uses the default (module) logger."""

    @logged(named_logger)
    class NestedClass(object):

        def __init__(self):
            self.__logger.info("message")

    @logged
    class _NonPublicNestedClass(object):

        def __init__(self):
            self.__logger.info("message")

    @logged
    class __MangledNestedClass(object):

        def __init__(self):
            self.__logger.info("message")

    @staticmethod
    def static_method():
        LoggedClass.__logger.info("message")

    @classmethod
    def class_method(cls):
        cls.__logger.info("message")

    def instance_method(self):
        self.__logger.info("message")

    def __eq__(self, other):
        self.__logger.info("message")
        return False


@logged
def logged_function():
    @logged(named_logger)
    def nested_function():
        nested_function._logger.info("message")
    logged_function._logger.info("message")
    return nested_function


@traced #t_f:L1
def traced_function(arg, keyword=None):
    @traced(named_tracer)   #n_f:L1
    def nested_function():
        return "%s and %s" % (arg, keyword) #n_f:LN
    return nested_function  #t_f:LN


@logged #l_a_t_f:L1
@traced(named_tracer)
def logged_and_traced_function():
    logged_and_traced_function._logger.info("message")  #l_a_t_f:LN


if (_is_py3):
    from test._dummy3 import (
        _TracedParent,
        LoggedAndTracedClass,
        ModuleLoggerExplicitTracedClass,
        ModuleLoggerImplicitSpecialTracedClass,
        ModuleLoggerImplicitTracedClass,
        NamedTracerExplicitTracedClass,
        NamedTracerImplicitSpecialTracedClass,
        NamedTracerImplicitTracedClass,
        NonTracedChildTracedParent,
        TracedChildNonTracedParent,
        TracedChildTracedParent,
    )
    from test import (
        dummy3_module_logger as dummyM_module_logger,
        get_dummy3_lineno as get_dummyM_lineno,
    )
else:
    from test._dummy2 import (
        _TracedParent,
        LoggedAndTracedClass,
        ModuleLoggerExplicitTracedClass,
        ModuleLoggerImplicitSpecialTracedClass,
        ModuleLoggerImplicitTracedClass,
        NamedTracerExplicitTracedClass,
        NamedTracerImplicitSpecialTracedClass,
        NamedTracerImplicitTracedClass,
        NonTracedChildTracedParent,
        TracedChildNonTracedParent,
        TracedChildTracedParent,
    )
    from test import (
        dummy2_module_logger as dummyM_module_logger,
        get_dummy2_lineno as get_dummyM_lineno,
    )

