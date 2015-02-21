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

"""Python 3 dummy classes and functions for testing :mod:`autologging`."""

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.4.0"

import logging

from autologging import logged, TracedMethods

from test import named_tracer

__all__ = [
    "LoggedAndTracedClass",
    "ModuleLoggerExplicitTracedClass",
    "ModuleLoggerImplicitSpecialTracedClass",
    "ModuleLoggerImplicitTracedClass",
    "NamedTracerExplicitTracedClass",
    "NamedTracerImplicitSpecialTracedClass",
    "NamedTracerImplicitTracedClass",
    "NonTracedChildTracedParent",
    "TracedChildNonTracedParent",
    "TracedChildTracedParent",
]


class ModuleLoggerImplicitTracedClass(metaclass=TracedMethods()):

    class NestedNamedTracerExplicitTracedClass(
            metaclass=TracedMethods(named_tracer, "class_method", "method")):

        @staticmethod
        def static_method(arg, keyword=None):
            return "%s and %s" % (arg, keyword)

        FORMAT_STRING = "%s and %s"

        @classmethod    #MLITC.NNTETC.c_m:L1
        def class_method(cls, arg, keyword=None):
            return cls.FORMAT_STRING % (arg, keyword)   #MLITC.NNTETC.c_m:LN

        def __init__(self):
            self.format_string = "%s and %s"

        def method(self, arg, keyword=None):   #MLITC.NNTETC.m:L1
            return self.format_string % (arg, keyword)  #MLITC.NNTETC.m:LN

    @staticmethod   #MLITC.s_m:L1
    def static_method(arg, keyword=None):
        return "%s and %s" % (arg, keyword) #MLITC.s_m:LN

    FORMAT_STRING = "%s and %s"

    @classmethod    #MLITC.c_m:L1
    def class_method(cls, arg, keyword=None):
        return cls.FORMAT_STRING % (arg, keyword)   #MLITC.c_m:LN

    def __init__(self): #MLITC.__i__:L1
        self.format_string = "%s and %s"    #MLITC.__i__:LN

    def method(self, arg, keyword=None):   #MLITC.m:L1
        return self.format_string % (arg, keyword)  #MLITC.m:LN

    def __eq__(self, other):
        return False


class ModuleLoggerImplicitSpecialTracedClass(
        metaclass=TracedMethods(trace_special_methods=True)):

    def __init__(self): #MLISTC.__i__:L1
        self.format_string = "%s and %s"    #MLISTC.__i__:LN

    def method(self, arg, keyword=None):    #MLISTC.m:L1
        return self.format_string % (arg, keyword)  #MLISTC.m:LN

    def _nonpublic(self, arg, keyword=None): #MLISTC._n:L1
        return self.format_string % (arg, keyword)  #MLISTC._n:LN

    def __private(self, arg, keyword=None): #MLISTC.__p:L1
        return self.format_string % (arg, keyword)  #MLISTC.__p:LN

    def __eq__(self, other):    #MLISTC.__e__:L1
        return False    #MLISTC.__e__:LN


class ModuleLoggerExplicitTracedClass(
        metaclass=TracedMethods("static_method", "__init__", "_nonpublic",
                                "__private", trace_special_methods=True)):

    @staticmethod   #MLETC.s_m:L1
    def static_method(arg, keyword=None):
        return "%s and %s" % (arg, keyword) #MLETC.s_m:LN

    FORMAT_STRING = "%s and %s"

    @classmethod
    def class_method(cls, arg, keyword=None):
        return cls.FORMAT_STRING % (arg, keyword)

    def __init__(self): #MLETC.__i__:L1
        self.format_string = "%s and %s"    #MLETC.__i__:LN

    def method(self, arg, keyword=None):
        return self.format_string % (arg, keyword)

    def _nonpublic(self, arg, keyword=None): #MLETC._n:L1
        return self.format_string % (arg, keyword)  #MLETC._n:LN

    def __private(self, arg, keyword=None): #MLETC.__p:L1
        return self.format_string % (arg, keyword)  #MLETC.__p:LN

    # trace_special_methods is ignored when methods are explicitly traced
    def __eq__(self, other):
        return False


class NamedTracerImplicitTracedClass(metaclass=TracedMethods(named_tracer)):

    class NestedModuleLoggerExplicitTracedClass(
            metaclass=TracedMethods("static_method", "method")):

        @staticmethod   #NTITC.NMLETC.s_m:L1
        def static_method(arg, keyword=None):
            return "%s and %s" % (arg, keyword) #NTITC.NMLETC.s_m:LN

        FORMAT_STRING = "%s and %s"

        @classmethod
        def class_method(cls, arg, keyword=None):
            return cls.FORMAT_STRING % (arg, keyword)

        def __init__(self):
            self.format_string = "%s and %s"

        def method(self, arg, keyword=None):   #NTITC.NMLETC.m:L1
            return self.format_string % (arg, keyword)  #NTITC.NMLETC.m:LN

    @staticmethod   #NTITC.s_m:L1
    def static_method(arg, keyword=None):
        return "%s and %s" % (arg, keyword) #NTITC.s_m:LN

    FORMAT_STRING = "%s and %s"

    @classmethod    #NTITC.c_m:L1
    def class_method(cls, arg, keyword=None):
        return cls.FORMAT_STRING % (arg, keyword)   #NTITC.c_m:LN

    def __init__(self): #NTITC.__i__:L1
        self.format_string = "%s and %s"    #NTITC.__i__:LN

    def method(self, arg, keyword=None):   #NTITC.m:L1
        return self.format_string % (arg, keyword)  #NTITC.m:LN

    def __eq__(self, other):
        return False


class NamedTracerImplicitSpecialTracedClass(
        metaclass=TracedMethods(named_tracer, trace_special_methods=True)):

    FORMAT_STRING = "%s and %s"

    def method(self, arg, keyword=None):    #NTISTC.m:L1
        return self.FORMAT_STRING % (arg, keyword)  #NTISTC.m:LN

    def _nonpublic(self, arg, keyword=None): #NTISTC._n:L1
        return self.FORMAT_STRING % (arg, keyword)  #NTISTC._n:LN

    def __private(self, arg, keyword=None): #NTISTC.__p:L1
        return self.FORMAT_STRING % (arg, keyword)  #NTISTC.__p:LN

    def __eq__(self, other):    #NTISTC.__e__:L1
        return False    #NTISTC.__e__:LN


class NamedTracerExplicitTracedClass(
        metaclass=TracedMethods(named_tracer, "class_method", "_nonpublic",
                                "__private", "__eq__")):

    @staticmethod
    def static_method(arg, keyword=None):
        return "%s and %s" % (arg, keyword)

    FORMAT_STRING = "%s and %s"

    @classmethod    #NTETC.c_m:L1
    def class_method(cls, arg, keyword=None):
        return cls.FORMAT_STRING % (arg, keyword)   #NTETC.c_m:LN

    def __init__(self):
        self.format_string = "%s and %s"

    def method(self, arg, keyword=None):
        return self.format_string % (arg, keyword)

    def _nonpublic(self, arg, keyword=None): #NTETC._n:L1
        return self.format_string % (arg, keyword)  #NTETC._n:LN

    def __private(self, arg, keyword=None): #NTETC.__p:L1
        return self.format_string % (arg, keyword)  #NTETC.__p:LN

    def __eq__(self, other):    #NTETC.__e__:L1
        return False    #NTETC.__e__:LN


class _TracedParent(metaclass=TracedMethods()):

    @staticmethod
    def static_method():
        return 'static'

    CLASS = 'class'

    @classmethod
    def class_method(cls):
        return cls.CLASS

    def __init__(self): #_TP.__i__:L1
        self.instance = 'instance'  #_TP.__i__:LN

    def method(self):   #_TP.m:L1
        return self.instance    #_TP.m:LN


class NonTracedChildTracedParent(_TracedParent):

    def method(self):
        return super().method().upper()


class _NonTracedParent:

    @staticmethod
    def static_method():
        return 'static'

    CLASS = 'class'

    @classmethod
    def class_method(cls):
        return cls.CLASS

    def __init__(self):
        self.instance = 'instance'

    def method(self):
        return self.instance


class TracedChildNonTracedParent(_NonTracedParent, metaclass=TracedMethods()):

    def method(self):   #TCNTP.m:L1
        return super().method().upper() #TCNTP.m:LN


class TracedChildTracedParent(_TracedParent, metaclass=TracedMethods()):

    def method(self):   #TCTP.m:L1
        return super().method().upper() #TCTP.m:LN


@logged
class LoggedAndTracedClass(metaclass=TracedMethods(named_tracer)):

    def method(self):   #LATC.m:L1
        self.__logger.info("message")   #LATC.m:LN

