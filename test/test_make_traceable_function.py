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
:func:`autologging._make_traceable_function`.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import logging
import unittest

from autologging import _make_traceable_function, TRACE, __version__

from test import list_handler, named_tracer

# suppress messages to the console
logging.getLogger().setLevel(logging.FATAL + 1)


def sample_function():
    pass


class MakeTraceableFunctionTest(unittest.TestCase):
    """Test the :func:`autologging._make_traceable_function`
    function.

    """

    def setUp(self):
        list_handler.reset()
        named_tracer.setLevel(logging.NOTSET)

    def test_wraps_original_function(self):
        delegator = _make_traceable_function(sample_function, named_tracer)
        self.assertTrue(delegator.__wrapped__ is sample_function)

    def test_uses_specified_logger(self):
        delegator = _make_traceable_function(sample_function, named_tracer)
        self.assertTrue(delegator._tracing_proxy.logger is named_tracer)

    def test_with_trace_enabled_emits_log_records(self):
        named_tracer.setLevel(TRACE)
        delegator = _make_traceable_function(sample_function, named_tracer)
        # IronPython gets func.__code__.co_freevars and func.__closure__ wrong
        # --------------------------------------------------------------------
        """
        print >> "\n\nfreevars and closure info:\n"
        for (i, name) in enumerate(delegator.__code__.co_freevars):
            print "%d:%s is" % (i, name), delegator.__closure__[i].cell_contents 
        """
        delegator()

        self.assertEqual(2, len(list_handler.records))

        call_record = list_handler.records[0]
        self.assertEqual(delegator.__wrapped__.__name__, call_record.funcName)
        self.assertEqual("CALL *() **{}", call_record.getMessage())
        return_record = list_handler.records[1]
        self.assertEqual(delegator.__wrapped__.__name__, return_record.funcName)
        self.assertEqual("RETURN None", return_record.getMessage())

    def test_with_trace_disabled_does_not_emit_records(self):
        named_tracer.setLevel(logging.DEBUG)
        delegator = _make_traceable_function(sample_function, named_tracer)
        delegator()

        self.assertEqual(0, len(list_handler.records))


def suite():
    return unittest.makeSuite(MakeTraceableFunctionTest)


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

