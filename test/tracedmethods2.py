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

"""Python 2 example class using the :func:`autologging.TracedMethods`
metaclass factory.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.1"

import logging

from autologging import TracedMethods


class ModuleLoggerTracedClass(object):
    __metaclass__ = TracedMethods("traced_staticmethod", "traced_classmethod",
                                  "traced_instancemethod")

    @staticmethod
    def traced_staticmethod(arg, keyword=None):
        """ModuleLoggerTracedClass static method."""
        return "%s and %s" % (arg, keyword)

    @classmethod
    def traced_classmethod(cls, arg, keyword=None):
        """ModuleLoggerTracedClass class method."""
        return "%s and %s" % (arg, keyword)

    def traced_instancemethod(self, arg, keyword=None):
        """ModuleLoggerTracedClass instance method."""
        return "%s and %s" % (arg, keyword)

    def nontraced_method(self):
        return "nothing to see here"


_named_logger = logging.getLogger("traced.methods.testing")


class NamedLoggerTracedClass(object):
    __metaclass__ = TracedMethods(_named_logger, "traced_staticmethod",
                                  "traced_classmethod",
                                  "traced_instancemethod")

    @staticmethod
    def traced_staticmethod(arg, keyword=None):
        """NamedLoggerTracedClass static method."""
        return "%s and %s" % (arg, keyword)

    @classmethod
    def traced_classmethod(cls, arg, keyword=None):
        """NamedLoggerTracedClass class method."""
        return "%s and %s" % (arg, keyword)

    def traced_instancemethod(self, arg, keyword=None):
        """NamedLoggerTracedClass instance method."""
        return "%s and %s" % (arg, keyword)

    def nontraced_method(self):
        return "nothing to see here"
