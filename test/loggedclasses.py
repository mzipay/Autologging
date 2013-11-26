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

"""Example classes that have been decorated with
:func:`autologging.logged`.

"""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.2"

import logging

from autologging import logged


@logged
class ModuleLoggerClass(object):
    """Uses the default (module) logger."""

    @staticmethod
    def logged_staticmethod():
        """ModuleLoggerClass static method."""
        ModuleLoggerClass.__logger.info(
            "ModuleLoggerClass.logged_staticmethod test.")

    @classmethod
    def logged_classmethod(cls):
        """ModuleLoggerClass class method."""
        cls.__logger.info("ModuleLoggerClass.logged_classmethod test.")

    def logged_instancemethod(self):
        """ModuleLoggerClass instance method."""
        self.__logger.info("ModuleLoggerClass.logged_instancemethod test.")


_named_logger = logging.getLogger("logged.testing")


@logged(_named_logger)
class NamedLoggerClass(object):
    """"Uses a specifically-named logger."""

    @staticmethod
    def logged_staticmethod():
        """NamedLoggerClass static method."""
        NamedLoggerClass.__logger.info(
            "NamedLoggerClass.logged_staticmethod test.")

    @classmethod
    def logged_classmethod(cls):
        """NamedLoggerClass class method."""
        cls.__logger.info("NamedLoggerClass.logged_classmethod test.")

    def logged_instancemethod(self):
        """NamedLoggerClass instance method."""
        self.__logger.info("NamedLoggerClass.logged_instancemethod test.")


class OuterClass(object):
    """Test a logged inner class."""

    @logged
    class InnerClass(object):
        pass


@logged
class _InternalClass(object):
    """Test an internal-named class and inner class."""

    @logged
    class _InnerInternalClass(object):
        pass
