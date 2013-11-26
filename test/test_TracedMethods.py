# -*- coding: utf-8 -*-

# Copyright (c) 2013 Matthew Zipay <mattz@ninthtest.net>
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

"""Test cases and runner for the :func:`autologging.TracedMethods`
metaclass factory.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.1"

import logging
import os
import sys
import unittest

from autologging import TRACE
from test import ListHandler

if (sys.version_info.major >= 3):
    from test.tracedmethods3 import (ModuleLoggerTracedClass,
                                     NamedLoggerTracedClass)
else:
    from test.tracedmethods2 import (ModuleLoggerTracedClass,
                                     NamedLoggerTracedClass)

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


class ModuleLoggerTracedMethodsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._handler = ListHandler(level=TRACE)
        for method_name in ["traced_staticmethod", "traced_classmethod",
                            "traced_instancemethod"]:
            method = getattr(ModuleLoggerTracedClass, method_name)
            # the testing handler needs to be added to the logger proxy, which
            # is a free variable of the method tracer closure
            closure_index = \
                method.__code__.co_freevars.index("logger_proxy")
            logger_proxy = \
                method.__closure__[closure_index].cell_contents
            logger_proxy.setLevel(TRACE)
            logger_proxy.addHandler(cls._handler)
        cls.expected_name = ("%s.ModuleLoggerTracedClass" %
                             ModuleLoggerTracedClass.__module__)  # @UndefinedVariable
        cls.expected_levelname = "TRACE"
        cls.expected_levelno = TRACE
        # fetch the expected pathname from one of the original methods (not the
        # tracer proxy methods); the originals are available as free variables
        # of the method tracer closures
        closure_index = \
            ModuleLoggerTracedClass.traced_instancemethod.__code__.co_freevars.index("method")  # @UndefinedVariable
        method = \
            ModuleLoggerTracedClass.traced_instancemethod.__closure__[closure_index].cell_contents
        cls.expected_pathname = method.__code__.co_filename
        cls.expected_filename = os.path.basename(cls.expected_pathname)
        cls.expected_module = os.path.splitext(cls.expected_filename)[0]

    def test_traced_staticmethod_call(self):
        value = \
            ModuleLoggerTracedClass.traced_staticmethod("spam", keyword="eggs")
        self.assertEqual("spam and eggs", value)
        return_record = self._handler.records.pop()
        call_record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, call_record.name)
        self.assertEqual(self.expected_levelname, call_record.levelname)
        self.assertEqual(self.expected_levelno, call_record.levelno)
        self.assertEqual(self.expected_pathname, call_record.pathname)
        self.assertEqual(self.expected_filename, call_record.filename)
        self.assertEqual(self.expected_module, call_record.module)
        self.assertEqual(40, call_record.lineno)
        self.assertEqual("traced_staticmethod", call_record.funcName)
        self.assertEqual(
            "CALL ModuleLoggerTracedClass.traced_staticmethod *('spam',) **{'keyword': 'eggs'}",
            call_record.getMessage())
        self.assertEqual(self.expected_name, return_record.name)
        self.assertEqual(self.expected_levelname, return_record.levelname)
        self.assertEqual(self.expected_levelno, return_record.levelno)
        self.assertEqual(self.expected_pathname, return_record.pathname)
        self.assertEqual(self.expected_filename, return_record.filename)
        self.assertEqual(self.expected_module, return_record.module)
        self.assertEqual(43, return_record.lineno)
        self.assertEqual("traced_staticmethod", return_record.funcName)
        self.assertEqual(
            "RETURN ModuleLoggerTracedClass.traced_staticmethod 'spam and eggs'",
            return_record.getMessage())

    def test_traced_staticmethod_magicattrs(self):
        self.assertEqual(
            ModuleLoggerTracedClass.__module__,  # @UndefinedVariable
            ModuleLoggerTracedClass.traced_staticmethod.__module__,  # @UndefinedVariable
            "ModuleLoggerTracedClass.traced_staticmethod.__module__")
        self.assertEqual(
            "traced_staticmethod",
            ModuleLoggerTracedClass.traced_staticmethod.__name__,  # @UndefinedVariable
            "ModuleLoggerTracedClass.traced_staticmethod.__name__")
        self.assertEqual("ModuleLoggerTracedClass static method.",
                         ModuleLoggerTracedClass.traced_staticmethod.__doc__,
                         "ModuleLoggerTracedClass.traced_staticmethod.__doc__")
        if (sys.version_info.major >= 3):
            self.assertEqual(
                dict(),
                ModuleLoggerTracedClass.traced_staticmethod.__annotations__,  # @UndefinedVariable
                "ModuleLoggerTracedClass.traced_staticmethod.__annotations__")
            if (sys.version_info.minor >= 3):
                self.assertEqual(
                    "ModuleLoggerTracedClass.traced_staticmethod",
                    ModuleLoggerTracedClass.traced_staticmethod.__qualname__,  # @UndefinedVariable
                    "ModuleLoggerTracedClass.traced_staticmethod.__qualname__")

    def test_traced_classmethod_call(self):
        value = ModuleLoggerTracedClass.traced_classmethod("green eggs",
                                                           keyword="ham")
        self.assertEqual("green eggs and ham", value)
        return_record = self._handler.records.pop()
        call_record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, call_record.name)
        self.assertEqual(self.expected_levelname, call_record.levelname)
        self.assertEqual(self.expected_levelno, call_record.levelno)
        self.assertEqual(self.expected_pathname, call_record.pathname)
        self.assertEqual(self.expected_filename, call_record.filename)
        self.assertEqual(self.expected_module, call_record.module)
        self.assertEqual(45, call_record.lineno)
        self.assertEqual("traced_classmethod", call_record.funcName)
        self.assertEqual(
            "CALL ModuleLoggerTracedClass.traced_classmethod *('green eggs',) **{'keyword': 'ham'}",
            call_record.getMessage())
        self.assertEqual(self.expected_name, return_record.name)
        self.assertEqual(self.expected_levelname, return_record.levelname)
        self.assertEqual(self.expected_levelno, return_record.levelno)
        self.assertEqual(self.expected_pathname, return_record.pathname)
        self.assertEqual(self.expected_filename, return_record.filename)
        self.assertEqual(self.expected_module, return_record.module)
        self.assertEqual(48, return_record.lineno)
        self.assertEqual("traced_classmethod", return_record.funcName)
        self.assertEqual(
            "RETURN ModuleLoggerTracedClass.traced_classmethod 'green eggs and ham'",
            return_record.getMessage())

    def test_traced_classmethod_magicattrs(self):
        self.assertEqual(
            ModuleLoggerTracedClass.__module__,  # @UndefinedVariable
            ModuleLoggerTracedClass.traced_classmethod.__module__,  # @UndefinedVariable
            "ModuleLoggerTracedClass.traced_classmethod.__module__")
        self.assertEqual(
            "traced_classmethod",
            ModuleLoggerTracedClass.traced_classmethod.__name__,  # @UndefinedVariable
            "ModuleLoggerTracedClass.traced_classmethod.__name__")
        self.assertEqual("ModuleLoggerTracedClass class method.",
                         ModuleLoggerTracedClass.traced_classmethod.__doc__,
                         "ModuleLoggerTracedClass.traced_classmethod.__doc__")
        if (sys.version_info.major >= 3):
            self.assertEqual(
                dict(),
                ModuleLoggerTracedClass.traced_classmethod.__annotations__,  # @UndefinedVariable
                "ModuleLoggerTracedClass.traced_classmethod.__annotations__")
            if (sys.version_info.minor >= 3):
                self.assertEqual(
                    "ModuleLoggerTracedClass.traced_classmethod",
                    ModuleLoggerTracedClass.traced_classmethod.__qualname__,  # @UndefinedVariable
                    "ModuleLoggerTracedClass.traced_classmethod.__qualname__")

    def test_traced_instancemethod_call(self):
        instance = ModuleLoggerTracedClass()
        value = instance.traced_instancemethod("Batman", keyword="Robin")
        self.assertEqual("Batman and Robin", value)
        return_record = self._handler.records.pop()
        call_record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, call_record.name)
        self.assertEqual(self.expected_levelname, call_record.levelname)
        self.assertEqual(self.expected_levelno, call_record.levelno)
        self.assertEqual(self.expected_pathname, call_record.pathname)
        self.assertEqual(self.expected_filename, call_record.filename)
        self.assertEqual(self.expected_module, call_record.module)
        self.assertEqual(50, call_record.lineno)
        self.assertEqual("traced_instancemethod", call_record.funcName)
        self.assertEqual(
            "CALL ModuleLoggerTracedClass.traced_instancemethod *('Batman',) **{'keyword': 'Robin'}",
            call_record.getMessage())
        self.assertEqual(self.expected_name, return_record.name)
        self.assertEqual(self.expected_levelname, return_record.levelname)
        self.assertEqual(self.expected_levelno, return_record.levelno)
        self.assertEqual(self.expected_pathname, return_record.pathname)
        self.assertEqual(self.expected_filename, return_record.filename)
        self.assertEqual(self.expected_module, return_record.module)
        self.assertEqual(52, return_record.lineno)
        self.assertEqual("traced_instancemethod", return_record.funcName)
        self.assertEqual(
            "RETURN ModuleLoggerTracedClass.traced_instancemethod 'Batman and Robin'",
            return_record.getMessage())

    def test_traced_instancemethod_magicattrs(self):
        self.assertEqual(
            ModuleLoggerTracedClass.__module__,  # @UndefinedVariable
            ModuleLoggerTracedClass.traced_instancemethod.__module__,  # @UndefinedVariable
            "ModuleLoggerTracedClass.traced_instancemethod.__module__")
        self.assertEqual(
            "traced_instancemethod",
            ModuleLoggerTracedClass.traced_instancemethod.__name__,  # @UndefinedVariable
            "ModuleLoggerTracedClass.traced_instancemethod.__name__")
        self.assertEqual("ModuleLoggerTracedClass instance method.",
                         ModuleLoggerTracedClass.traced_instancemethod.__doc__,
                         "ModuleLoggerTracedClass.traced_instancemethod.__doc__")
        if (sys.version_info.major >= 3):
            self.assertEqual(
                dict(),
                ModuleLoggerTracedClass.traced_instancemethod.__annotations__,  # @UndefinedVariable
                "ModuleLoggerTracedClass.traced_instancemethod.__annotations__")
            if (sys.version_info.minor >= 3):
                self.assertEqual(
                    "ModuleLoggerTracedClass.traced_instancemethod",
                    ModuleLoggerTracedClass.traced_instancemethod.__qualname__,  # @UndefinedVariable
                    "ModuleLoggerTracedClass.traced_instancemethod.__qualname__")

    def test_nontraced_method_call(self):
        instance = ModuleLoggerTracedClass()
        value = instance.nontraced_method()
        self.assertEqual("nothing to see here", value)
        self.assertEqual(0, len(self._handler.records),
                         repr(self._handler.records))


class NamedLoggerTracedMethodsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._handler = ListHandler(level=TRACE)
        for method_name in ["traced_staticmethod", "traced_classmethod",
                            "traced_instancemethod"]:
            method = getattr(NamedLoggerTracedClass, method_name)
            # the testing handler needs to be added to the logger proxy, which
            # is a free variable of the method tracer closure
            closure_index = \
                method.__code__.co_freevars.index("logger_proxy")
            logger_proxy = \
                method.__closure__[closure_index].cell_contents
            logger_proxy.setLevel(TRACE)
            logger_proxy.addHandler(cls._handler)
        cls.expected_name = "traced.methods.testing.NamedLoggerTracedClass"
        cls.expected_levelname = "TRACE"
        cls.expected_levelno = TRACE
        # fetch the expected pathname from one of the original methods (not the
        # tracer proxy methods); the originals are available as free variables
        # of the method tracer closures
        closure_index = \
            NamedLoggerTracedClass.traced_instancemethod.__code__.co_freevars.index("method")  # @UndefinedVariable
        method = \
            NamedLoggerTracedClass.traced_instancemethod.__closure__[closure_index].cell_contents
        cls.expected_pathname = method.__code__.co_filename
        cls.expected_filename = os.path.basename(cls.expected_pathname)
        cls.expected_module = os.path.splitext(cls.expected_filename)[0]

    def test_traced_staticmethod_call(self):
        value = \
            NamedLoggerTracedClass.traced_staticmethod("spam", keyword="eggs")
        self.assertEqual("spam and eggs", value)
        return_record = self._handler.records.pop()
        call_record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, call_record.name)
        self.assertEqual(self.expected_levelname, call_record.levelname)
        self.assertEqual(self.expected_levelno, call_record.levelno)
        self.assertEqual(self.expected_pathname, call_record.pathname)
        self.assertEqual(self.expected_filename, call_record.filename)
        self.assertEqual(self.expected_module, call_record.module)
        self.assertEqual(66, call_record.lineno)
        self.assertEqual("traced_staticmethod", call_record.funcName)
        self.assertEqual(
            "CALL NamedLoggerTracedClass.traced_staticmethod *('spam',) **{'keyword': 'eggs'}",
            call_record.getMessage())
        self.assertEqual(self.expected_name, return_record.name)
        self.assertEqual(self.expected_levelname, return_record.levelname)
        self.assertEqual(self.expected_levelno, return_record.levelno)
        self.assertEqual(self.expected_pathname, return_record.pathname)
        self.assertEqual(self.expected_filename, return_record.filename)
        self.assertEqual(self.expected_module, return_record.module)
        self.assertEqual(69, return_record.lineno)
        self.assertEqual("traced_staticmethod", return_record.funcName)
        self.assertEqual(
            "RETURN NamedLoggerTracedClass.traced_staticmethod 'spam and eggs'",
            return_record.getMessage())

    def test_traced_staticmethod_magicattrs(self):
        self.assertEqual(
            NamedLoggerTracedClass.__module__,  # @UndefinedVariable
            NamedLoggerTracedClass.traced_staticmethod.__module__,  # @UndefinedVariable
            "NamedLoggerTracedClass.traced_staticmethod.__module__")
        self.assertEqual(
            "traced_staticmethod",
            NamedLoggerTracedClass.traced_staticmethod.__name__,  # @UndefinedVariable
            "NamedLoggerTracedClass.traced_staticmethod.__name__")
        self.assertEqual("NamedLoggerTracedClass static method.",
                         NamedLoggerTracedClass.traced_staticmethod.__doc__,
                         "NamedLoggerTracedClass.traced_staticmethod.__doc__")
        if (sys.version_info.major >= 3):
            self.assertEqual(
                dict(),
                NamedLoggerTracedClass.traced_staticmethod.__annotations__,  # @UndefinedVariable
                "NamedLoggerTracedClass.traced_staticmethod.__annotations__")
            if (sys.version_info.minor >= 3):
                self.assertEqual(
                    "NamedLoggerTracedClass.traced_staticmethod",
                    NamedLoggerTracedClass.traced_staticmethod.__qualname__,  # @UndefinedVariable
                    "NamedLoggerTracedClass.traced_staticmethod.__qualname__")

    def test_traced_classmethod_call(self):
        value = NamedLoggerTracedClass.traced_classmethod("green eggs",
                                                          keyword="ham")
        self.assertEqual("green eggs and ham", value)
        return_record = self._handler.records.pop()
        call_record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, call_record.name)
        self.assertEqual(self.expected_levelname, call_record.levelname)
        self.assertEqual(self.expected_levelno, call_record.levelno)
        self.assertEqual(self.expected_pathname, call_record.pathname)
        self.assertEqual(self.expected_filename, call_record.filename)
        self.assertEqual(self.expected_module, call_record.module)
        self.assertEqual(71, call_record.lineno)
        self.assertEqual("traced_classmethod", call_record.funcName)
        self.assertEqual(
            "CALL NamedLoggerTracedClass.traced_classmethod *('green eggs',) **{'keyword': 'ham'}",
            call_record.getMessage())
        self.assertEqual(self.expected_name, return_record.name)
        self.assertEqual(self.expected_levelname, return_record.levelname)
        self.assertEqual(self.expected_levelno, return_record.levelno)
        self.assertEqual(self.expected_pathname, return_record.pathname)
        self.assertEqual(self.expected_filename, return_record.filename)
        self.assertEqual(self.expected_module, return_record.module)
        self.assertEqual(74, return_record.lineno)
        self.assertEqual("traced_classmethod", return_record.funcName)
        self.assertEqual(
            "RETURN NamedLoggerTracedClass.traced_classmethod 'green eggs and ham'",
            return_record.getMessage())

    def test_traced_classmethod_magicattrs(self):
        self.assertEqual(
            NamedLoggerTracedClass.__module__,  # @UndefinedVariable
            NamedLoggerTracedClass.traced_classmethod.__module__,  # @UndefinedVariable
            "NamedLoggerTracedClass.traced_classmethod.__module__")
        self.assertEqual(
            "traced_classmethod",
            NamedLoggerTracedClass.traced_classmethod.__name__,  # @UndefinedVariable
            "NamedLoggerTracedClass.traced_classmethod.__name__")
        self.assertEqual("NamedLoggerTracedClass class method.",
                         NamedLoggerTracedClass.traced_classmethod.__doc__,
                         "NamedLoggerTracedClass.traced_classmethod.__doc__")
        if (sys.version_info.major >= 3):
            self.assertEqual(
                dict(),
                NamedLoggerTracedClass.traced_classmethod.__annotations__,  # @UndefinedVariable
                "NamedLoggerTracedClass.traced_classmethod.__annotations__")
            if (sys.version_info.minor >= 3):
                self.assertEqual(
                    "NamedLoggerTracedClass.traced_classmethod",
                    NamedLoggerTracedClass.traced_classmethod.__qualname__,  # @UndefinedVariable
                    "NamedLoggerTracedClass.traced_classmethod.__qualname__")

    def test_traced_instancemethod_call(self):
        instance = NamedLoggerTracedClass()
        value = instance.traced_instancemethod("Batman", keyword="Robin")
        self.assertEqual("Batman and Robin", value)
        return_record = self._handler.records.pop()
        call_record = self._handler.records.pop()
        self.assertEqual(0, len(self._handler.records),
                          repr(self._handler.records))
        self.assertEqual(self.expected_name, call_record.name)
        self.assertEqual(self.expected_levelname, call_record.levelname)
        self.assertEqual(self.expected_levelno, call_record.levelno)
        self.assertEqual(self.expected_pathname, call_record.pathname)
        self.assertEqual(self.expected_filename, call_record.filename)
        self.assertEqual(self.expected_module, call_record.module)
        self.assertEqual(76, call_record.lineno)
        self.assertEqual("traced_instancemethod", call_record.funcName)
        self.assertEqual(
            "CALL NamedLoggerTracedClass.traced_instancemethod *('Batman',) **{'keyword': 'Robin'}",
            call_record.getMessage())
        self.assertEqual(self.expected_name, return_record.name)
        self.assertEqual(self.expected_levelname, return_record.levelname)
        self.assertEqual(self.expected_levelno, return_record.levelno)
        self.assertEqual(self.expected_pathname, return_record.pathname)
        self.assertEqual(self.expected_filename, return_record.filename)
        self.assertEqual(self.expected_module, return_record.module)
        self.assertEqual(78, return_record.lineno)
        self.assertEqual("traced_instancemethod", return_record.funcName)
        self.assertEqual(
            "RETURN NamedLoggerTracedClass.traced_instancemethod 'Batman and Robin'",
            return_record.getMessage())

    def test_traced_instancemethod_magicattrs(self):
        self.assertEqual(
            NamedLoggerTracedClass.__module__,  # @UndefinedVariable
            NamedLoggerTracedClass.traced_instancemethod.__module__,  # @UndefinedVariable
            "NamedLoggerTracedClass.traced_instancemethod.__module__")
        self.assertEqual(
            "traced_instancemethod",
            NamedLoggerTracedClass.traced_instancemethod.__name__,  # @UndefinedVariable
            "NamedLoggerTracedClass.traced_instancemethod.__name__")
        self.assertEqual("NamedLoggerTracedClass instance method.",
                         NamedLoggerTracedClass.traced_instancemethod.__doc__,
                         "NamedLoggerTracedClass.traced_instancemethod.__doc__")
        if (sys.version_info.major >= 3):
            self.assertEqual(
                dict(),
                NamedLoggerTracedClass.traced_instancemethod.__annotations__,  # @UndefinedVariable
                "NamedLoggerTracedClass.traced_instancemethod.__annotations__")
            if (sys.version_info.minor >= 3):
                self.assertEqual(
                    "NamedLoggerTracedClass.traced_instancemethod",
                    NamedLoggerTracedClass.traced_instancemethod.__qualname__,  # @UndefinedVariable
                    "NamedLoggerTracedClass.traced_instancemethod.__qualname__")

    def test_nontraced_method_call(self):
        instance = NamedLoggerTracedClass()
        value = instance.nontraced_method()
        self.assertEqual("nothing to see here", value)
        self.assertEqual(0, len(self._handler.records),
                         repr(self._handler.records))


def suite():
    """Build the test suite for :func:`autologging.TracedMethods`."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModuleLoggerTracedMethodsTest))
    suite.addTest(unittest.makeSuite(NamedLoggerTracedMethodsTest))
    return suite


if (__name__ == "__main__"):
    unittest.TextTestRunner().run(suite())
