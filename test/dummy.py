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

"""Dummy classes and functions used in Autologging functional tests."""

__author__ = "Matthew Zipay <mattz@ninthtest.info>"

import sys

from autologging import logged, traced, __version__

from test import named_logger, named_tracer


@logged
def logged_function():
    @logged(named_logger)
    def nested_function():
        nested_function._log.info("l_f.n_f message")
    logged_function._log.info("l_f message")
    return nested_function


@logged
class LoggedClass(object):

    @logged
    class NestedClass(object):

        def __init__(self):
            self.__log.info("LC.NC.__i__ message")

    @logged(named_logger)
    class __InternalNestedClass(object):

        def __init__(self):
            self.__log.info("LC.__INC.__i__ message")

    @staticmethod
    def static_method():
        LoggedClass.__log.info("LC.s_m message")

    @classmethod
    def class_method(cls):
        cls.__log.info("LC.c_m message")

    def __init__(self):
        self.__log.info("LC.__i__ message")


@traced #t_f:L1
def traced_function(arg, keyword=None):
    @traced(named_tracer)   #t_f.n_f:L1
    def nested_function(arg, keyword=None):
        return "t_f.n_f %s and %s" % (arg, keyword) #t_f.n_f:LN
    return nested_function  #t_f:LN


@traced
class TracedClass(object):

    ABBREV = "TC"

    @traced
    class NestedClass(object):

        def __init__(self): #TC.NC.__i__:L1
            self.format_string = "TC.NC.%s %s and %s"

    @traced(named_tracer, "method")
    class __InternalNestedClass(object):

        def __init__(self):
            self.format_string = "TC.__INC.%s %s and %s"

        def method(self, arg, keyword=None):    #TC.__INC.m:L1
            return self.format_string % ('m', arg, keyword) #TC.__INC.m:LN

    @staticmethod   #TC.s_m:L1
    def static_method(arg, keyword=None):
        return "TC.s_m %s and %s" % (arg, keyword)  #TC.s_m:LN

    @classmethod    #TC.c_m:L1
    def class_method(cls, arg, keyword=None):
        return "%s.c_m %s and %s" % (cls.ABBREV, arg, keyword)  #TC.c_m:LN

    def __init__(self): #TC.__i__:L1
        self.format_string = "TC.%s %s and %s"

    def __call__(self): #TC.__c__:L1
        return "TC.__call__" #TC.__c__:LN


@logged #l_a_t_f:L1
@traced(named_tracer)
def logged_and_traced_function(arg, keyword=None):
    @traced #l_a_t_f.n_t_a_l_f:L1
    @logged(named_logger)
    def nested_traced_and_logged_function(arg, keyword=None):
        nested_traced_and_logged_function._log.info("l_a_t_f.n_t_a_l_f message")
        return "l_a_t_f.n_t_a_l_f %s and %s" % (arg, keyword)   #l_a_t_f.n_t_a_l_f:LN
    logged_and_traced_function._log.info("l_a_t_f message")
    return nested_traced_and_logged_function    #l_a_t_f:LN


@logged
@traced("method")
class LoggedAndTracedClass:

    @logged(named_logger)
    @traced
    class NestedClass:

        def __init__(self): #LATC.NC.__i__:L1
            self.__log.info("LATC.NC.__i__ message")

        def __call__(self, arg): #LATC.NC.__c__:L1
            self.__log.info("LATC.NC.__c__ message")
            return "LATC.NC.__call__ %s" % arg   #LATC.NC.__c__:LN

    @logged
    @traced(named_tracer)
    class _NonPublicNestedClass:

        def __init__(self): #LATC._NPNC.__i__:L1
            self.__log.info("LATC._NPNC.__i__ message")

    @traced(named_tracer, "method")
    @logged(named_logger)
    class __InternalNestedClass:

        def __init__(self):
            self.format_string = "LATC.__INC.%s %s and %s"
            self.__log.info("LATC.__INC.__i__ message")

        def method(self, arg, keyword=None):    #LATC.__INC.m:L1
            self.__log.info("LATC.__INC.m message")
            return self.format_string % ('m', arg, keyword) #LATC.__INC.m:LN

    def __init__(self):
        self.__log.info("LATC.__i__ message")
        self.format_string = "LATC.%s %s and %s"

    def method(self, arg, keyword=None):    #LATC.m:L1
        self.__log.info("LATC.m message")
        return self.format_string % ('m', arg, keyword) #LATC.m:LN


@traced
class _TracedParent(object):

    def inherited_method(self, arg, keyword=None):  #_TP.i_m:L1
        return "_TP.i_m %s and %s" % (arg, keyword) #_TP.i_m:LN

    def overridden_method(self, arg, keyword=None): #_TP.o_m:L1
        return "_TP.o_m %s and %s" % (arg, keyword)  #_TP.o_m:LN


class _NonTracedParent(object):

    def inherited_method(self, arg, keyword=None):
        return "_NTP.i_m %s and %s" % (arg, keyword)

    def overridden_method(self, arg, keyword=None):
        return "_NTP.o_m %s and %s" % (arg, keyword)


class NonTracedChildTracedParent(_TracedParent):

    def overridden_method(self, arg, keyword=None):
        return "%s NTCTP.o_m" % \
            super(NonTracedChildTracedParent, self).overridden_method(
                arg, keyword=keyword)


@traced
class TracedChildNonTracedParent(_NonTracedParent):

    def overridden_method(self, arg, keyword=None): #TCNTP.o_m:L1
        parent_return_value = \
            super(TracedChildNonTracedParent, self).overridden_method(
                arg, keyword=keyword)
        return "%s TCNTP.o_m" % parent_return_value #TCNTP.o_m:LN


@traced
class TracedChildTracedParent(_TracedParent):

    def overridden_method(self, arg, keyword=None): #TCTP.o_m:L1
        parent_return_value = \
            super(TracedChildTracedParent, self).overridden_method(
                arg, keyword=keyword)
        return "%s TCTP.o_m" % parent_return_value  #TCTP.o_m:LN


@traced
class GeneratorClass(object):

    @staticmethod   #GC.s_g:L1
    def static_generator(v):
        for c in reversed(v):
            yield c #GC.s_g:LY  #GC.s_g:LN

    @classmethod    #GC.c_g:L1
    def class_generator(cls, v):
        for c in reversed(v):
            yield c #GC.c_g:LY  #GC.c_g:LN

    def method_generator(self, v):  #GC.m_g:L1
        for c in reversed(v):
            yield c #GC.m_g:LY  #GC.m_g:LN


@traced #t_g:L1
def traced_generator(v):
    for c in reversed(v):
        yield c #t_g:LY
    # `yield' might not be the last instruction in a generator!
    pass    #t_g:LN

