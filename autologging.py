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

__author__ = "Matthew Zipay <mattz@ninthtest.net>"
__version__ = "0.3.0"

from functools import wraps
import logging
import types

__all__ = [
    "logged",
    "TRACE",
    "traced",
    "TracedMethods",
]

#: A custom tracing log level, lower in severity than :py:data:`logging.DEBUG`.
#: Autologging :func:`traced` and :func:`TracedMethods` create log records
#: with this custom level.
TRACE = 1
logging.addLevelName(TRACE, "TRACE")


def logged(obj):
    """Add a named logger member to a decorated class or function.

    The logger member always has a dot-separated name consisting of the
    parent logger's name, followed by a dot ('.'), followed by the class
    or function name.

    If *obj* is a :py:class:`class`, then ``obj.__logger`` will have
    the logger name "module-name.class-name":

    >>> @logged
    ... class Test:
    ...     pass
    ... 
    >>> Test._Test__logger.name
    'autologging.Test'

    Similarly for functions:

    >>> @logged
    ... def test():
    ...     pass
    ... 
    >>> test.__logger.name
    'autologging.test'

    If *obj* is a :py:class:`logging.Logger` object, then that logger is
    treated as the parent logger and the decorated class's ``__logger``
    member will have the logger name "parent-logger-name.class-name":

    >>> _logger = logging.getLogger("test.parent")
    >>> @logged(_logger)
    ... class Test:
    ...     pass
    ... 
    >>> Test._Test__logger.name
    'test.parent.Test'

    Again, functions are similar.

    >>> _logger = logging.getLogger("test.parent")
    >>> @logged(_logger)
    ... def test_fn():
    ...     pass
    ... 
    >>> test_fn.__logger.name
    'test.parent.test_fn'

    .. note::

        For classes, the logger member is made "private" (i.e. ``__logger``
        with double underscore) to ensure that log messages that include the
        *%(name)s* format placeholder are written with the correct
        name.

        Consider a subclass of a ``@logged``-decorated parent class. If
        the subclass were **not** decorated with ``@logged`` and could
        access the parent's logger member directly to make logging
        calls, those log messages would display the name of the
        **parent** class, not the subclass. 

        Therefore, subclasses of a ``@logged``-decorated parent class
        that wish to use a provided ``self.__logger`` object **must**
        themselves be decorated with ``@logged``.

    .. note::

        Within a logged function, the ``__logger`` attribute must be
        qualified by the function name, i.e. "function-name.__logger":

        >>> @logged
        ... def do_something():
        ...     do_something.__logger.info('Doing something')
        ...

    """
    def add_logger_to(obj, parent):
        if (hasattr(obj, "__qualname__")):
            logger_name = obj.__qualname__
        else:
            logger_name = obj.__name__
        logger = logging.getLogger("%s.%s" % (parent, logger_name))

        if isinstance(obj, types.FunctionType):
            obj.__dict__['__logger'] = logger
            return obj
        else:
            setattr(obj, "_%s__logger" % obj.__name__.lstrip('_'), logger)
            return obj

    if (isinstance(obj, logging.Logger)):
        # decorated as `@logged(logger)' - use logger as parent
        return lambda class_or_fn: add_logger_to(class_or_fn, obj.name)
    else:
        # decorated as `@logged' - use module logger as parent
        return add_logger_to(obj, obj.__module__)


def traced(obj):
    """Add call/return tracing to an unbound function.

    .. warning::

        This decorator will not quite work as expected (or may fail
        entirely) for class methods. To automatically trace class
        method call/return, please see the :class:`TracedMethods`
        metaclass factory.

    In the following example, tracing log messages are written to a
    log whose channel defaults to the function's module name:

    >>> import sys
    >>> logging.basicConfig(level=TRACE, stream=sys.stdout)
    >>> @traced
    ... def my_function(arg, keyword=None):
    ...     return "%s and %s" % (arg, keyword)
    ... 
    >>> my_function("spam", keyword="eggs")
    TRACE:autologging:CALL my_function *('spam',) **{'keyword': 'eggs'}
    TRACE:autologging:RETURN my_function 'spam and eggs'
    'spam and eggs'

    In the following example, tracing log messages are written to
    a user-named log:

    >>> import sys
    >>> logging.basicConfig(level=TRACE, stream=sys.stdout)
    >>> _logger = logging.getLogger("test.ing")
    >>> @traced(_logger)
    ... def my_function(arg, keyword=None):
    ...     return "%s and %s" % (arg, keyword)
    ... 
    >>> my_function("spam", keyword="eggs")
    TRACE:test.ing:CALL my_function *('spam',) **{'keyword': 'eggs'}
    TRACE:test.ing:RETURN my_function 'spam and eggs'
    'spam and eggs'

    """
    if (isinstance(obj, logging.Logger)):
        # decorated as `@traced(logger)' - log to logger
        logger = obj
        def traced_decorator(function):
            return _make_function_tracer(function, logger)
        return traced_decorator
    else:
        # decorated as `@traced' - log to module logger
        function = obj
        logger = logging.getLogger(function.__module__)
        return _make_function_tracer(function, logger)


def _make_function_tracer(function, logger):
    """Return a tracing proxy function for *function*.

    *function* is assumed to be an unbound, module-level function.

    *logger* is a :py:class:`logging.Logger` object to which tracing
    messages will be sent.

    """
    logger_proxy = _LoggerCallerProxy(logger, function)
    @wraps(function)
    def autologging_function_trace(*args, **keywords):
        if (logger_proxy.isEnabledFor(TRACE)):
            logger_proxy.autologging_call("%s *%r **%r", function.__name__,
                                          args, keywords)
            value = function(*args, **keywords)
            logger_proxy.autologging_return("%s %r", function.__name__, value)
            return value
        else:
            return function(*args, **keywords)
    return autologging_function_trace


def TracedMethods(*args):
    """Return a metaclass that enables call/return tracing for methods.

    Only methods named **explicitly** in *args* will be traced.

    If the **first** item in *args* is a :py:class:`logging.Logger`,
    then that logger is treated as the parent logger, and method tracers
    will use a logger with the name "parent-logger-name.class-name".
    Otherwise, method tracers will use a logger with the name
    "module-name.class-name".

    .. note::

        Regardless of whether a logger was explicitly passed in or not,
        the logger used by the tracers is **not** made available to the
        class or its instances.

        This allows for logging configurations where tracing is sent to
        a separate file/target than logging. For such a configuration,
        simply configure a logger specifically for tracing and pass that
        logger as the first argument to ``TracedMethods``.

        Also note that a class may be decorated by :func:`logged`
        **and** use ``TracedMethods`` as a metaclass without conflict.

    In the following example, tracing log messages are written to a
    log whose channel defaults to "module-name.class-name":

    >>> import sys
    >>> logging.basicConfig(level=TRACE, stream=sys.stdout)
    >>> class MyClass(object,
    ...               metaclass=TracedMethods("my_staticmethod",
    ...                                       "my_classmethod",
    ...                                       "my_instancemethod")):
    ...     @staticmethod
    ...     def my_staticmethod(arg, keyword=None):
    ...         return "%s and %s" % (arg, keyword)
    ...     @classmethod
    ...     def my_classmethod(cls, arg, keyword=None):
    ...         return "%s and %s" % (arg, keyword)
    ...     def my_instancemethod(self, arg, keyword=None):
    ...         return "%s and %s" % (arg, keyword)
    ... 
    >>> MyClass.my_staticmethod("spam", keyword="eggs")
    TRACE:autologging.MyClass:CALL MyClass.my_staticmethod *('spam',) **{'keyword': 'eggs'}
    TRACE:autologging.MyClass:RETURN MyClass.my_staticmethod 'spam and eggs'
    'spam and eggs'
    >>> MyClass.my_classmethod("green eggs", keyword="ham")
    TRACE:autologging.MyClass:CALL MyClass.my_classmethod *('green eggs',) **{'keyword': 'ham'}
    TRACE:autologging.MyClass:RETURN MyClass.my_classmethod 'green eggs and ham'
    'green eggs and ham'
    >>> instance = MyClass()
    >>> instance.my_instancemethod("Batman", keyword="Robin")
    TRACE:autologging.MyClass:CALL MyClass.my_instancemethod *('Batman',) **{'keyword': 'Robin'}
    TRACE:autologging.MyClass:RETURN MyClass.my_instancemethod 'Batman and Robin'
    'Batman and Robin'

    In the following example, tracing log messages are written to
    a user-named log:

    >>> import sys
    >>> logging.basicConfig(level=TRACE, stream=sys.stdout)
    >>> _logger = logging.getLogger("test.ing")
    >>> class MyClass(object,
    ...               metaclass=TracedMethods(_logger, "my_staticmethod",
    ...                                       "my_classmethod",
    ...                                       "my_instancemethod")):
    ...     @staticmethod
    ...     def my_staticmethod(arg, keyword=None):
    ...         return "%s and %s" % (arg, keyword)
    ...     @classmethod
    ...     def my_classmethod(cls, arg, keyword=None):
    ...         return "%s and %s" % (arg, keyword)
    ...     def my_instancemethod(self, arg, keyword=None):
    ...         return "%s and %s" % (arg, keyword)
    ... 
    >>> MyClass.my_staticmethod("spam", keyword="eggs")
    TRACE:test.ing.MyClass:CALL MyClass.my_staticmethod *('spam',) **{'keyword': 'eggs'}
    TRACE:test.ing.MyClass:RETURN MyClass.my_staticmethod 'spam and eggs'
    'spam and eggs'
    >>> MyClass.my_classmethod("green eggs", keyword="ham")
    TRACE:test.ing.MyClass:CALL MyClass.my_classmethod *('green eggs',) **{'keyword': 'ham'}
    TRACE:test.ing.MyClass:RETURN MyClass.my_classmethod 'green eggs and ham'
    'green eggs and ham'
    >>> instance = MyClass()
    >>> instance.my_instancemethod("Batman", keyword="Robin")
    TRACE:test.ing.MyClass:CALL MyClass.my_instancemethod *('Batman',) **{'keyword': 'Robin'}
    TRACE:test.ing.MyClass:RETURN MyClass.my_instancemethod 'Batman and Robin'
    'Batman and Robin'

    """
    class TracingMeta(type):
        def __new__(meta, name, bases, dict_):
            if (args and isinstance(args[0], logging.Logger)):
                logger = logging.getLogger("%s.%s" % (args[0].name, name))
                method_names = args[1:]
            else:
                logger = logging.getLogger("%s.%s" %
                                           (dict_["__module__"], name))
                method_names = args

            # replace each named method with a tracing proxy method
            for method_name in method_names:
                dict_[method_name] = _make_method_tracer(name,
                                                         dict_[method_name],
                                                         logger)
            return super(TracingMeta, meta).__new__(meta, name, bases, dict_)
    return TracingMeta


def _make_method_tracer(classname, method, logger):
    """Return a tracing proxy method for *method*.

    *method* can be an instance method, :py:class:`classmethod`, or
    :py:class:`staticmethod`.

    *logger* is a :py:class:`logging.Logger` object to which tracing
    messages will be sent.

    """
    if (type(method) is staticmethod):
        make_tracer = _make_staticmethod_tracer
    elif (type(method) is classmethod):
        make_tracer = _make_classmethod_tracer
    else:
        make_tracer = _make_instancemethod_tracer
    return make_tracer(classname, method, logger)


def _make_instancemethod_tracer(classname, method, logger):
    """Return a tracing proxy instance method for *method*.

    *classname* is the simple name of the class to which *method*
    belongs.

    *method* must be an instance method of the class named by
    *classname*.

    *logger* is a :py:class:`logging.Logger` object to which tracing
    messages will be sent.

    """
    logger_proxy = _LoggerCallerProxy(logger, method)
    dotted_name = "%s.%s" % (classname, method.__name__)
    @wraps(method)
    def autologging_instancemethod_trace(self, *args, **keywords):
        if (logger_proxy.isEnabledFor(TRACE)):
            logger_proxy.autologging_call("%s *%r **%r",
                                          dotted_name, args, keywords)
            value = method(self, *args, **keywords)
            logger_proxy.autologging_return("%s %r", dotted_name, value)
            return value
        else:
            return method(self, *args, **keywords)
    return autologging_instancemethod_trace


def _make_classmethod_tracer(classname, descriptor, logger):
    """Return a tracing proxy :py:class:`classmethod` for *descriptor*.

    *classname* is the simple name of the class to which *descriptor*
    belongs.

    *descriptor* must be a ``classmethod`` descriptor of the class named
    by *classname*.

    *logger* is a :py:class:`logging.Logger` object to which tracing
    messages will be sent.

    """
    function = descriptor.__get__(None, descriptor)
    logger_proxy = _LoggerCallerProxy(logger, function)
    dotted_name = "%s.%s" % (classname, function.__name__)
    @wraps(function)
    def autologging_classmethod_trace(cls, *args, **keywords):
        if (logger_proxy.isEnabledFor(TRACE)):
            logger_proxy.autologging_call("%s *%r **%r",
                                          dotted_name, args, keywords)
            value = function(*args, **keywords)
            logger_proxy.autologging_return("%s %r", dotted_name, value)
            return value
        else:
            return function(*args, **keywords)
    return classmethod(autologging_classmethod_trace)


def _make_staticmethod_tracer(classname, descriptor, logger):
    """Return a tracing proxy :py:class:`staticmethod` for *descriptor*.

    *classname* is the simple name of the class to which *descriptor*
    belongs.

    *descriptor* must be a ``staticmethod`` descriptor of the class
    named by *classname*.

    *logger* is a :py:class:`logging.Logger` object to which tracing
    messages will be sent.

    """
    function = descriptor.__get__(None, descriptor)
    logger_proxy = _LoggerCallerProxy(logger, function)
    dotted_name = "%s.%s" % (classname, function.__name__)
    @wraps(function)
    def autologging_staticmethod_trace(*args, **keywords):
        if (logger_proxy.isEnabledFor(TRACE)):
            logger_proxy.autologging_call("%s *%r **%r",
                                          dotted_name, args, keywords)
            value = function(*args, **keywords)
            logger_proxy.autologging_return("%s %r", dotted_name, value)
            return value
        else:
            return function(*args, **keywords)
    return staticmethod(autologging_staticmethod_trace)


class _LoggerCallerProxy(logging.getLoggerClass()):
    """A subclass that uses caller information from a proxied function.

    .. note::

        Without this subclass, tracing log messages would report caller
        information (filename, function name, etc.) of the proxy
        function rather than of the prox**ied** function.

    """

    def __init__(self, logger, proxied_function):
        """Impersonate *logger* and extract caller info from
        *proxied_function*.

        """
        super(_LoggerCallerProxy, self).__init__(logger.name,
                                                 level=logger.level)
        self.__dict__.update(logger.__dict__)

        # __code__ was backported to 2.7, but just to be safe...
        code = getattr(proxied_function, "func_code",
                       getattr(proxied_function, "__code__"))
        self._autologging_co_filename = code.co_filename
        self._autologging_co_firstlineno = code.co_firstlineno
        self._autologging_co_lastlineno = _find_last_line_number(code)
        self._autologging_co_name = code.co_name
        self.findCaller = self.autologging_findCaller

    def autologging_call(self, msg, *args, **kwargs):
        """Log a :data:`TRACE`-level message that a function is called.

        The *msg*, *args*, and *kwargs* arguments are the same as for
        :py:func:`logging.Logger.log` (but note that the literal string
        "CALL " will be automatically prepended to *msg*).

        """
        if (self.isEnabledFor(TRACE)):
            msg = "CALL " + msg
            self._autologging_f_lineno = self._autologging_co_firstlineno
            super(_LoggerCallerProxy, self).log(TRACE, msg, *args, **kwargs)

    def autologging_return(self, msg, *args, **kwargs):
        """Log a :data:`TRACE`-level message that a function returned.

        The *msg*, *args*, and *kwargs* arguments are the same as for
        :py:func:`logging.Logger.log` (but note that the literal string
        "RETURN " will be automatically prepended to *msg*).

        """
        if (self.isEnabledFor(TRACE)):
            msg = "RETURN " + msg
            self._autologging_f_lineno = self._autologging_co_lastlineno
            super(_LoggerCallerProxy, self).log(TRACE, msg, *args, **kwargs)

    def autologging_findCaller(self, *args, **keywords):
        """Return caller information used to construct a
        :py:class:`logging.LogRecord`.

        This method replaces :py:func:`logging.Logger.findCaller` to
        provide the filename, line number, and function name of a
        proxied function. (This information would be otherwise
        unavailable to a logger because it is inaccessible from
        stack frames.)

        """
        # keyword 'stack_info' was added in Python 3.2
        rv = super(_LoggerCallerProxy, self).findCaller(*args, **keywords)
        return (self._autologging_co_filename, self._autologging_f_lineno,
                self._autologging_co_name) + rv[3:]


def _find_last_line_number(func_code):
    """Return the last line number of a function.

    *func_code* is a :py:class:`types.CodeType` object (as obtained from
    ``some_function.__code__`` or ``some_function.func_code``).

    """
    last_line_number = func_code.co_firstlineno
    # co_lnotab is a sequence of 2-byte offsets (address offset, line number
    # offset), each relative to the previous; we only care about the line
    # number offsets here, so start at index 1 and increment by 2
    i = 1
    if (isinstance(func_code.co_lnotab, str)):
        # co_lnotab is str in Python 2
        while (i < len(func_code.co_lnotab)):
            last_line_number += ord(func_code.co_lnotab[i])
            i += 2
    else:
        # co_lnotab is bytes in Python 3
        while (i < len(func_code.co_lnotab)):
            last_line_number += func_code.co_lnotab[i]
            i += 2
    return last_line_number
