# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2015, 2016, 2018, 2019 Matthew Zipay.
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
:func:`autologging._GeneratorIteratorTracingProxy`.

"""

__author__ = "Matthew Zipay (mattzATninthtestDOTinfo)"

from inspect import isgenerator
import logging
import unittest

from autologging import (
    _is_jython,
    _is_ironpython,
    TRACE,
    _GeneratorIteratorTracingProxy,
    __version__,
)

from test import get_lineno, list_handler

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


def gf(count): #gf:L1
    for i in range(count):
        yield i + 1 #gf:LY


_expected_function_filename = gf.__code__.co_filename
# generator iterators have a built-in reference to a frame object, so the
# line number *should* be consistent... except for IronPython
_expected_function_L1 = get_lineno(_expected_function_filename, "#gf:L1")
_expected_function_LY = (
        get_lineno(_expected_function_filename, "#gf:LY")
        if not _is_ironpython else _expected_function_L1)
_expected_function_LS = (
        _expected_function_L1
        if not _is_jython else (_expected_function_LY - 1))


class Class(object):

    def gm(self, count): #C.gm:L1
        for i in range(count):
            yield i + 1 #C.gm:LY


_method = Class.__dict__["gm"]
_expected_method_filename = _method.__code__.co_filename
# generator iterators have a built-in reference to a frame object, so the
# line number *should* be consistent... except for IronPython
_expected_method_L1 = get_lineno(_expected_method_filename, "#C.gm:L1")
_expected_method_LY = (
        get_lineno(_expected_method_filename, "#C.gm:LY")
        if not _is_ironpython else _expected_method_L1)
_expected_method_LS = (
        _expected_method_L1
        if not _is_jython else (_expected_method_LY - 1))

_module_logger = logging.getLogger(__name__)
_module_logger.setLevel(TRACE)
_module_logger.addHandler(list_handler)

_class_logger = logging.getLogger(__name__ + ".Class")
_class_logger.propagate = False
_class_logger.setLevel(TRACE)
_class_logger.addHandler(list_handler)


class TestException(Exception):
    pass


class GeneratorIteratorTracingProxyTest(unittest.TestCase):
    """Test the
    :class:`autologging._GeneratorIteratorTracingProxy` class.

    """

    def setUp(self):
        list_handler.reset()

    def test_function_yield1_log_record(self):
        gi = gf(2)
        proxy = _GeneratorIteratorTracingProxy(gf, gi, _module_logger)

        self.assertEqual(1, next(proxy))
        self.assertEqual(1, len(list_handler.records))

        record = list_handler.records[0]
        self.assertEqual(_module_logger.name, record.name)
        self.assertEqual("YIELD %r %r", record.msg)
        self.assertEqual((gi, 1,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_function_filename, record.pathname)
        self.assertEqual(_expected_function_LY, record.lineno)
        self.assertEqual("gf", record.funcName)

    def test_function_yield2_log_record(self):
        gi = gf(2)
        proxy = _GeneratorIteratorTracingProxy(gf, gi, _module_logger)

        self.assertEqual(1, next(proxy))
        self.assertEqual(2, next(proxy))
        self.assertEqual(2, len(list_handler.records))

        record = list_handler.records[1]
        self.assertEqual(_module_logger.name, record.name)
        self.assertEqual("YIELD %r %r", record.msg)
        self.assertEqual((gi, 2,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_function_filename, record.pathname)
        self.assertEqual(_expected_function_LY, record.lineno)
        self.assertEqual("gf", record.funcName)

    def test_function_stop_log_record(self):
        gi = gf(2)
        proxy = _GeneratorIteratorTracingProxy(gf, gi, _module_logger)

        self.assertEqual(1, next(proxy))
        self.assertEqual(2, next(proxy))
        self.assertRaises(StopIteration, next, proxy)
        self.assertEqual(3, len(list_handler.records))

        record = list_handler.records[2]
        self.assertEqual(_module_logger.name, record.name)
        self.assertEqual("STOP %r", record.msg)
        self.assertEqual((gi,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_function_filename, record.pathname)
        self.assertEqual(_expected_function_LS, record.lineno)
        self.assertEqual("gf", record.funcName)

    def test_function_send_log_record(self):
        gi = gf(2)
        proxy = _GeneratorIteratorTracingProxy(gf, gi, _module_logger)

        # proxy.send(None) should be equivalent to next(proxy)
        self.assertEqual(1, proxy.send(None))
        self.assertEqual(1, len(list_handler.records))

        record = list_handler.records[0]
        self.assertEqual(_module_logger.name, record.name)
        self.assertEqual("SEND %r %r", record.msg)
        self.assertEqual((gi, None,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_function_filename, record.pathname)
        # in Jython, the generator iterator doesn't even have a line number
        # at this point (it's 0)
        self.assertEqual(_expected_function_L1 if not _is_jython else 0,
                record.lineno)
        self.assertEqual("gf", record.funcName)

    def test_function_throw_log_record(self):
        gi = gf(2)
        proxy = _GeneratorIteratorTracingProxy(gf, gi, _module_logger)
        testex = TestException("test")

        self.assertRaises(TestException, proxy.throw, testex)
        self.assertEqual(1, len(list_handler.records))

        record = list_handler.records[0]
        self.assertEqual(_module_logger.name, record.name)
        self.assertEqual("THROW %r %r", record.msg)
        self.assertEqual((gi, testex,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_function_filename, record.pathname)
        # in Jython, the generator iterator doesn't even have a line number
        # at this point (it's 0)
        self.assertEqual(_expected_function_L1 if not _is_jython else 0,
                record.lineno)
        self.assertEqual("gf", record.funcName)

    def test_function_close_log_record(self):
        gi = gf(2)
        proxy = _GeneratorIteratorTracingProxy(gf, gi, _module_logger)

        proxy.close()
        self.assertRaises(StopIteration, next, proxy)
        self.assertEqual(2, len(list_handler.records)) # CLOSE, STOP

        record = list_handler.records[0]
        self.assertEqual(_module_logger.name, record.name)
        self.assertEqual("CLOSE %r", record.msg)
        self.assertEqual((gi,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_function_filename, record.pathname)
        # in Jython, the generator iterator doesn't even have a line number
        # at this point (it's 0)
        self.assertEqual(_expected_function_L1 if not _is_jython else 0,
                record.lineno)
        self.assertEqual("gf", record.funcName)

    def test_method_yield1_log_record(self):
        obj = Class()
        gi = obj.gm(2)
        proxy = _GeneratorIteratorTracingProxy(obj.gm, gi, _class_logger)

        self.assertEqual(1, next(proxy))
        self.assertEqual(1, len(list_handler.records))

        record = list_handler.records[0]
        self.assertEqual(_class_logger.name, record.name)
        self.assertEqual("YIELD %r %r", record.msg)
        self.assertEqual((gi, 1,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_method_filename, record.pathname)
        self.assertEqual(_expected_method_LY, record.lineno)
        self.assertEqual("gm", record.funcName)

    def test_method_yield2_log_record(self):
        obj = Class()
        gi = obj.gm(2)
        proxy = _GeneratorIteratorTracingProxy(obj.gm, gi, _class_logger)

        self.assertEqual(1, next(proxy))
        self.assertEqual(2, next(proxy))
        self.assertEqual(2, len(list_handler.records))

        record = list_handler.records[1]
        self.assertEqual(_class_logger.name, record.name)
        self.assertEqual("YIELD %r %r", record.msg)
        self.assertEqual((gi, 2,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_method_filename, record.pathname)
        self.assertEqual(_expected_method_LY, record.lineno)
        self.assertEqual("gm", record.funcName)

    def test_method_stop_log_record(self):
        obj = Class()
        gi = obj.gm(2)
        proxy = _GeneratorIteratorTracingProxy(obj.gm, gi, _class_logger)

        self.assertEqual(1, next(proxy))
        self.assertEqual(2, next(proxy))
        self.assertRaises(StopIteration, next, proxy)
        self.assertEqual(3, len(list_handler.records))

        record = list_handler.records[2]
        self.assertEqual(_class_logger.name, record.name)
        self.assertEqual("STOP %r", record.msg)
        self.assertEqual((gi,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_method_filename, record.pathname)
        self.assertEqual(_expected_method_LS, record.lineno)
        self.assertEqual("gm", record.funcName)

    def test_method_send_log_record(self):
        obj = Class()
        gi = obj.gm(2)
        proxy = _GeneratorIteratorTracingProxy(obj.gm, gi, _class_logger)

        # proxy.send(None) should be equivalent to next(proxy)
        self.assertEqual(1, proxy.send(None))
        self.assertEqual(1, len(list_handler.records))

        record = list_handler.records[0]
        self.assertEqual(_class_logger.name, record.name)
        self.assertEqual("SEND %r %r", record.msg)
        self.assertEqual((gi, None,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_method_filename, record.pathname)
        # in Jython, the generator iterator doesn't even have a line number
        # at this point (it's 0)
        self.assertEqual(_expected_method_L1 if not _is_jython else 0,
                record.lineno)
        self.assertEqual("gm", record.funcName)

    def test_method_throw_log_record(self):
        obj = Class()
        gi = obj.gm(2)
        proxy = _GeneratorIteratorTracingProxy(obj.gm, gi, _class_logger)
        testex = TestException("test")

        self.assertRaises(TestException, proxy.throw, testex)
        self.assertEqual(1, len(list_handler.records))

        record = list_handler.records[0]
        self.assertEqual(_class_logger.name, record.name)
        self.assertEqual("THROW %r %r", record.msg)
        self.assertEqual((gi, testex,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_method_filename, record.pathname)
        # in Jython, the generator iterator doesn't even have a line number
        # at this point (it's 0)
        self.assertEqual(_expected_method_L1 if not _is_jython else 0,
                record.lineno)
        self.assertEqual("gm", record.funcName)

    def test_method_close_log_record(self):
        obj = Class()
        gi = obj.gm(2)
        proxy = _GeneratorIteratorTracingProxy(obj.gm, gi, _class_logger)

        proxy.close()
        self.assertRaises(StopIteration, next, proxy)
        self.assertEqual(2, len(list_handler.records)) # CLOSE, STOP

        record = list_handler.records[0]
        self.assertEqual(_class_logger.name, record.name)
        self.assertEqual("CLOSE %r", record.msg)
        self.assertEqual((gi,), record.args)
        self.assertEqual("TRACE", record.levelname)
        self.assertEqual(TRACE, record.levelno)
        self.assertEqual(_expected_method_filename, record.pathname)
        # in Jython, the generator iterator doesn't even have a line number
        # at this point (it's 0)
        self.assertEqual(_expected_method_L1 if not _is_jython else 0,
                record.lineno)
        self.assertEqual("gm", record.funcName)


def suite():
    return unittest.makeSuite(GeneratorIteratorTracingProxyTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

