# -*- coding: utf-8 -*-

# Copyright (c) 2013, 2015, 2016 Matthew Zipay.
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

__author__ = (
    "Matthew Zipay <mattz@ninthtest.net>, "
    "Simon Knopp <simon.knopp@pg.canterbury.ac.nz>")
__version__ = "1.1.0"

from functools import wraps
from inspect import isclass, isroutine
import logging
import os
import sys
from types import FunctionType
import warnings

__all__ = [
    "TRACE",
    "logged",
    "traced",
    "install_traced_noop",
]

#: A custom tracing log level, lower in severity than :attr:`logging.DEBUG`.
TRACE = 1
logging.addLevelName(TRACE, "TRACE")


def logged(obj):
    """Add a logger member to a decorated class or function.

    :param obj: the class or function object being decorated, or an
                optional :class:`logging.Logger` object to be used as
                the parent logger (instead of the default module-named
                logger)
    :return: *obj* if *obj* is a class or function; otherwise, if *obj*
             is a logger, returns a lambda decorator that will in turn
             set the logger attribute and return *obj*

    If *obj* is a :obj:`class`, then ``obj.__log`` will have the logger
    name "<module-name>.<class-name>":

    >>> import sys
    >>> logging.basicConfig(
    ...     level=logging.DEBUG, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @logged
    ... class Sample:
    ...
    ...     def test(self):
    ...         self.__log.debug("This is a test.")
    ...
    >>> Sample().test()
    DEBUG:autologging.Sample:test:This is a test.

    .. note::
       Autologging will prefer to use the class's ``__qualname__`` when
       it is available (Python 3.3+). Otherwise, the class's
       ``__name__`` is used. For example::

          class Outer:

             @logged
             class Nested: pass

       Under Python 3.3+, ``Nested.__log`` will have the name
       "autologging.Outer.Nested", while under Python 2.7 or 3.2, the
       logger name will be "autologging.Nested".

    .. versionchanged:: 0.4.0
       Functions decorated with ``@logged`` use a *single* underscore
       in the logger variable name (e.g. ``my_function._log``) rather
       than a double underscore.

    If *obj* is a function, then ``obj._log`` will have the logger name
    "<module-name>":

    >>> import sys
    >>> logging.basicConfig(
    ...     level=logging.DEBUG, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @logged
    ... def test():
    ...     test._log.debug("This is a test.")
    ...
    >>> test()
    DEBUG:autologging:test:This is a test.

    .. note::
       Within a logged function, the ``_log`` attribute must be
       qualified by the function name.

    If *obj* is a :class:`logging.Logger` object, then that logger is
    used as the parent logger (instead of the default module-named
    logger):

    >>> import sys
    >>> logging.basicConfig(
    ...     level=logging.DEBUG, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @logged(logging.getLogger("test.parent"))
    ... class Sample:
    ...     def test(self):
    ...         self.__log.debug("This is a test.")
    ...
    >>> Sample().test()
    DEBUG:test.parent.Sample:test:This is a test.

    Again, functions are similar:

    >>> import sys
    >>> logging.basicConfig(
    ...     level=logging.DEBUG, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @logged(logging.getLogger("test.parent"))
    ... def test():
    ...     test._log.debug("This is a test.")
    ...
    >>> test()
    DEBUG:test.parent:test:This is a test.

    .. note::
       For classes, the logger member is made "private" (i.e. ``__log``
       with double underscore) to ensure that log messages that include
       the *%(name)s* format placeholder are written with the correct
       name.

       Consider a subclass of a ``@logged``-decorated parent class. If
       the subclass were **not** decorated with ``@logged`` and could
       access the parent's logger member directly to make logging
       calls, those log messages would display the name of the
       parent class, not the subclass.

       Therefore, subclasses of a ``@logged``-decorated parent class
       that wish to use a provided ``self.__log`` object must themselves
       be decorated with ``@logged``.

    .. warning::
       Although the ``@logged`` and ``@traced`` decorators will "do the
       right thing" regardless of the order in which they are applied to
       the same function, it is recommended that ``@logged`` always be
       used as the innermost decorator::

          @traced
          @logged
          def my_function():
              my_function._log.info("message")

       This is because ``@logged`` simply sets the ``_log`` attribute
       and then returns the original function, making it "safe" to use
       in combination with any other decorator.

    .. note::
       Both `Jython <http://www.jython.org/>`_ and
       `IronPython <http://ironpython.net/>`_ report an "internal" class
       name using its mangled form, which will be reflected in the
       default logger name.

       For example, in the sample code below, both Jython and IronPython
       will use the default logger name "autologging._Outer__Nested"
       (whereas CPython/PyPy/Stackless would use "autologging.__Nested"
       under Python 2 or "autologging.Outer.__Nested" under Python 3.3+)
       ::

          class Outer:
             @logged
             class __Nested:
                pass

    .. warning::
       `IronPython <http://ironpython.net/>`_ does not fully support
       frames (even with the -X:FullFrames option), so you are likely to
       see things like misreported line numbers and "<unknown file>" in
       log records emitted when running under IronPython.

    """
    if isinstance(obj, logging.Logger): # `@logged(logger)'
        return lambda class_or_fn: _add_logger_to(
            class_or_fn,
            logger_name=_generate_logger_name(
                class_or_fn, parent_name=obj.name))
    else: # `@logged'
        return _add_logger_to(obj)


def traced(*args):
    """Add call and return tracing to an unbound function or to the
    methods of a class.

    The arguments to ``traced`` differ depending on whether it is being
    used to trace an unbound function or the methods of a class:

    .. rubric:: Trace an unbound function using the default logger

    :param func: the unbound function to be traced

    By default, a logger named for the function's module is used:

    >>> import sys
    >>> logging.basicConfig(
    ...     level=TRACE, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @traced
    ... def func(x, y):
    ...     return x + y
    ...
    >>> func(7, 9)
    TRACE:autologging:func:CALL *(7, 9) **{}
    TRACE:autologging:func:RETURN 16
    16

    .. rubric:: Trace an unbound function using a named logger

    :param logging.Logger logger: the parent logger used to trace the\
                                  unbound function

    >>> import sys
    >>> logging.basicConfig(
    ...     level=TRACE, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @traced(logging.getLogger("my.channel"))
    ... def func(x, y):
    ...     return x + y
    ...
    >>> func(7, 9)
    TRACE:my.channel:func:CALL *(7, 9) **{}
    TRACE:my.channel:func:RETURN 16
    16

    .. rubric:: Trace default methods using the default logger

    :param class_: the class whose methods will be traced

    By default, all "public", "_nonpublic", and "__internal" methods, as
    well as the special "__init__" method, will be traced. Tracing log
    entries will be written to a logger named for the module and class:

    >>> import sys
    >>> logging.basicConfig(
    ...     level=TRACE, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @traced
    ... class Class:
    ...     def __init__(self, x):
    ...         self._x = x
    ...     def public(self, y):
    ...         return self._x + y
    ...     def _nonpublic(self, y):
    ...         return self._x - y
    ...     def __internal(self, y=2):
    ...         return self._x ** y
    ...     def __repr__(self):
    ...         return "Class(%r)" % self._x
    ...
    >>> obj = Class(7)
    TRACE:autologging.Class:__init__:CALL *(7,) **{}
    >>> obj.public(9)
    TRACE:autologging.Class:public:CALL *(9,) **{}
    TRACE:autologging.Class:public:RETURN 16
    16
    >>> obj._nonpublic(5)
    TRACE:autologging.Class:_nonpublic:CALL *(5,) **{}
    TRACE:autologging.Class:_nonpublic:RETURN 2
    2
    >>> obj._Class__internal(y=3)
    TRACE:autologging.Class:__internal:CALL *() **{'y': 3}
    TRACE:autologging.Class:__internal:RETURN 343
    343
    >>> repr(obj) # not traced by default
    'Class(7)'

    .. note::
       When the runtime Python version is >= 3.3, the *qualified* class
       name will be used to name the tracing logger (i.e. a nested class
       will write tracing log entries to a logger named
       "module.Parent.Nested").

    .. rubric:: Trace default methods using a named logger

    :param logging.Logger logger: the parent logger used to trace the
                                  methods of the class

    By default, all "public", "_nonpublic", and "__internal" methods, as
    well as the special "__init__" method, will be traced. Tracing log
    entries will be written to the specified logger:

    >>> import sys
    >>> logging.basicConfig(
    ...     level=TRACE, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @traced(logging.getLogger("my.channel"))
    ... class Class:
    ...     def __init__(self, x):
    ...         self._x = x
    ...     def public(self, y):
    ...         return self._x + y
    ...     def _nonpublic(self, y):
    ...         return self._x - y
    ...     def __internal(self, y=2):
    ...         return self._x ** y
    ...     def __repr__(self):
    ...         return "Class(%r)" % self._x
    ...
    >>> obj = Class(7)
    TRACE:my.channel.Class:__init__:CALL *(7,) **{}
    >>> obj.public(9)
    TRACE:my.channel.Class:public:CALL *(9,) **{}
    TRACE:my.channel.Class:public:RETURN 16
    16
    >>> obj._nonpublic(5)
    TRACE:my.channel.Class:_nonpublic:CALL *(5,) **{}
    TRACE:my.channel.Class:_nonpublic:RETURN 2
    2
    >>> obj._Class__internal(y=3)
    TRACE:my.channel.Class:__internal:CALL *() **{'y': 3}
    TRACE:my.channel.Class:__internal:RETURN 343
    343
    >>> repr(obj) # not traced by default
    'Class(7)'

    .. rubric:: Trace specified methods using the default logger

    :param tuple method_names: the names of the methods that will be
                               traced

    Tracing log entries will be written to a logger named for the
    module and class:

    >>> import sys
    >>> logging.basicConfig(
    ...     level=TRACE, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @traced("public", "__internal")
    ... class Class:
    ...     def __init__(self, x):
    ...         self._x = x
    ...     def public(self, y):
    ...         return self._x + y
    ...     def _nonpublic(self, y):
    ...         return self._x - y
    ...     def __internal(self, y=2):
    ...         return self._x ** y
    ...     def __repr__(self):
    ...         return "Class(%r)" % self._x
    ...
    >>> obj = Class(7)
    >>> obj.public(9)
    TRACE:autologging.Class:public:CALL *(9,) **{}
    TRACE:autologging.Class:public:RETURN 16
    16
    >>> obj._nonpublic(5)
    2
    >>> obj._Class__internal(y=3)
    TRACE:autologging.Class:__internal:CALL *() **{'y': 3}
    TRACE:autologging.Class:__internal:RETURN 343
    343
    >>> repr(obj)
    'Class(7)'

    .. warning::
       When method names are specified explicitly via *args*,
       Autologging ensures that each method is actually defined in
       the body of the class being traced. (This means that inherited
       methods that are not overridden are **never** traced, even if
       they are named explicitly in *args*.)

       If a defintion for any named method is not found in the class
       body, either because the method is inherited or because the
       name is misspelled, Autologging will issue a :exc:`UserWarning`.

       If you wish to trace a method from a super class, you have two
       options:

       1. Use ``traced`` to decorate the super class.
       2. Override the method and trace it in the subclass.

    .. note::
       When the runtime Python version is >= 3.3, the *qualified* class
       name will be used to name the tracig logger (i.e. a nested class
       will write tracing log entries to a logger named
       "module.Parent.Nested").

    .. rubric:: Trace specified methods using a named logger

    :param logging.Logger logger: the parent logger used to trace the
                                  methods of the class
    :param tuple method_names: the names of the methods that will be
                               traced

    >>> import sys
    >>> logging.basicConfig(
    ...     level=TRACE, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @traced(logging.getLogger("my.channel"), "public", "__internal")
    ... class Class:
    ...     def __init__(self, x):
    ...         self._x = x
    ...     def public(self, y):
    ...         return self._x + y
    ...     def _nonpublic(self, y):
    ...         return self._x - y
    ...     def __internal(self, y=2):
    ...         return self._x ** y
    ...     def __repr__(self):
    ...         return "Class(%r)" % self._x
    ...
    >>> obj = Class(7)
    >>> obj.public(9)
    TRACE:my.channel.Class:public:CALL *(9,) **{}
    TRACE:my.channel.Class:public:RETURN 16
    16
    >>> obj._nonpublic(5)
    2
    >>> obj._Class__internal(y=3)
    TRACE:my.channel.Class:__internal:CALL *() **{'y': 3}
    TRACE:my.channel.Class:__internal:RETURN 343
    343
    >>> repr(obj) # not traced by default
    'Class(7)'

    .. warning::
       When method names are specified explicitly via *args*,
       Autologging ensures that each method is actually defined in
       the body of the class being traced. (This means that inherited
       methods that are not overridden are **never** traced, even if
       they are named explicitly in *args*.)

       If a defintion for any named method is not found in the class
       body, either because the method is inherited or because the
       name is misspelled, Autologging will issue a :exc:`UserWarning`.

       If you wish to trace a method from a super class, you have two
       options:

       1. Use ``traced`` to decorate the super class.
       2. Override the method and trace it in the subclass.

    .. note::
       When tracing a class, if the default (class-named) logger is
       used **and** the runtime Python version is >= 3.3, then the
       *qualified* class name will be used to name the tracig logger
       (i.e. a nested class will write tracing log entries to a logger
       named "module.Parent.Nested").

    .. note::
       If method names are specified when decorating a function, a
       :exc:`UserWarning` is issued, but the methods names are ignored
       and the function is traced as though the method names had not
       been specified.

    .. note::
       Both `Jython <http://www.jython.org/>`_ and
       `IronPython <http://ironpython.net/>`_ report an "internal" class
       name using its mangled form, which will be reflected in the
       default tracing logger name.

       For example, in the sample code below, both Jython and IronPython
       will use the default tracing logger name
       "autologging._Outer__Nested" (whereas CPython/PyPy/Stackless
       would use "autologging.__Nested" under Python 2 or
       "autologging.Outer.__Nested" under Python 3.3+)::

          class Outer:
             @traced
             class __Nested:
                pass

    .. warning::
       Neither `Jython <http://www.jython.org/>`_ nor
       `IronPython <http://ironpython.net/>`_ currently implement the
       ``function.__code__.co_lnotab`` attribute, so the last line
       number of a function cannot be determined by Autologging.
       As a result, the line number reported in tracing RETURN log
       records will actually be the line number on which the function is
       defined.

    """
    obj = args[0] if args else None
    if obj is None:
        # treat `@traced()' as equivalent to `@traced'
        return traced

    if isclass(obj): # `@traced' class
        return _install_traceable_methods(obj)
    elif isroutine(obj): # `@traced' function
        return _make_traceable_function(
            obj, logging.getLogger(_generate_logger_name(obj)))
    elif isinstance(obj, logging.Logger):
        # may be decorating a class OR a function
        method_names = args[1:]

        def traced_decorator(class_or_fn):
            if isclass(class_or_fn):
                # `@traced(logger)' or `@traced(logger, "method_name1", ..)' class
                return _install_traceable_methods(
                    class_or_fn, *method_names,
                    logger=logging.getLogger(
                        _generate_logger_name(
                            class_or_fn, parent_name=obj.name)))
            else: # `@traced(logger)' function
                if method_names:
                    warnings.warn(
                        "ignoring method names for @traced function %s.%s" %
                            (class_or_fn.__module__, class_or_fn.__name__))
                return _make_traceable_function(class_or_fn, obj)

        return traced_decorator
    else: # `@traced("method_name1", ..)' class
        method_names = args[:]
        return lambda class_: _install_traceable_methods(class_, *method_names)


__traced_original = traced


def _traced_noop(*args):
    obj = args[0] if args else None
    if obj is None:
        # treat `@traced()' as equivalent to `@traced'
        return _traced_noop

    if isclass(obj) or isroutine(obj): # `@traced' class or function
        return obj
    else: # `@traced(logger)' or `@traced("method_name1", ..)'
        def traced_noop_decorator(class_or_fn):
            return class_or_fn

        return traced_noop_decorator


def install_traced_noop():
    """Replace the :func:`traced` decorator with an identity (no-op)
    decorator.

    Although the overhead of a ``@traced`` function or method is minimal
    when the :data:`TRACED` log level is disabled, there is still *some*
    overhead (the logging level check, an extra function call).

    If you would like to completely *eliminate* this overhead, call this
    function **before** any classes or functions in your application are
    decorated with ``@traced``. The :func:`traced` decorator will be
    replaced with a no-op decorator that simply returns the class or
    function unmodified.

    .. note::
       The **recommended** way to install the no-op ``@traced``
       decorator is to set the ``AUTOLOGGING_TRACED_NOOP``
       environment variable to any non-empty value.

       If the ``AUTOLOGGING_TRACED_NOOP`` environment variable is
       set to a non-empty value when Autologging is loaded, the
       ``@traced`` no-op will be installed automatically.

    As an alternative to setting the ``AUTOLOGGING_TRACED_NOOP``
    environment variable, you can also call this function directly in
    your application's bootstrap module. For example::

       import autologging

       if running_in_production:
           autologging.install_traced_noop()

    .. warning::
       This function **does not** "revert" any already-``@traced`` class
       or function! It simply replaces the ``autologging.traced`` module
       reference with a no-op.

       For this reason it is imperative that
       ``autologging.install_traced_noop()`` be called **before** the
       ``@traced`` decorator has been applied to any class or function
       in the application. (This is why the ``AUTOLOGGING_TRACED_NOOP``
       environment variable is the recommended approach for installing
       the no-op - it allows Autologging itself to guarantee that the
       no-op is installed before any classes or functions are
       decorated.)

    """
    global traced
    traced = _traced_noop
    logging.getLogger().info("autologging.traced no-op is installed")


if os.getenv("AUTOLOGGING_TRACED_NOOP"):
    install_traced_noop()


def _generate_logger_name(obj, parent_name=None):
    """Generate the logger name (channel) for a class or function.

    :param obj: a class or function
    :keyword str parent_name: the name of *obj*'s parent logger
    :rtype: str

    If *parent_name* is not specified, the default is to use *obj*'s
    module name.

    """
    parent_logger_name = parent_name if parent_name else obj.__module__
    return "%s.%s" % (
            parent_logger_name, getattr(obj, "__qualname__", obj.__name__)) \
        if isclass(obj) else parent_logger_name


def _add_logger_to(obj, logger_name=None):
    """Set a :class:`logging.Logger` member on *obj*.

    :param obj: a class or function object
    :keyword str logger_name: the name (channel) of the logger for *obj*
    :return: *obj*

    If *obj* is a class, the member will be named "__log". If *obj* is a
    function, the member will be named "_log".

    """
    logger = logging.getLogger(
        logger_name if logger_name else _generate_logger_name(obj))

    if isclass(obj):
        setattr(obj, _mangle_name("__log", obj.__name__), logger)
    else: # function
        obj._log = logger

    return obj


def _make_traceable_function(function, logger):
    """Return a tracing proxy function for *function*.

    :param function: an unbound, module-level (or nested) function
    :param logging.Logger logger: the logger for tracing messages
    :return: a proxy function that wraps *function* to provide the call
             and return tracing

    """
    log_delegator = _TracingLoggerDelegator(logger, function)

    @wraps(function)
    def autologging_traced_function_proxy(*args, **keywords):
        # don't access from closure (IronPython does not manage
        # co_freevars/__closure__ correctly)
        log_delegator = autologging_traced_function_proxy._trace_log_delegator
        if log_delegator.isEnabledFor(TRACE):
            log_delegator.trace_call(args, keywords)
            value = function(*args, **keywords)
            log_delegator.trace_return(value)
            return value
        else:
            return function(*args, **keywords)

    # NOT a logging.Logger subclass, but does implement read-only properties
    # and methods that mimic the public logging.Logger interface
    autologging_traced_function_proxy._trace_log_delegator = log_delegator

    if not hasattr(autologging_traced_function_proxy, "__wrapped__"):
        # __wrapped__ is only set by functools.wraps() in Python 3.2+
        autologging_traced_function_proxy.__wrapped__ = function

    autologging_traced_function_proxy.__autologging_traced__ = True

    return autologging_traced_function_proxy


# can't use option=<default> keywords with *args in Python 2.7 (see PEP-3102)
def _install_traceable_methods(class_, *method_names, **keywords):
    """Substitute tracing proxy methods for the methods named in
    *method_names* in *class_*'s ``__dict__``.

    :param class_: a class being traced
    :param tuple method_names: the names of the methods to be traced
    :keyword logging.Logger logger: the logger to use for tracing

    If *method_names* is empty, all "public", "_nonpublic", and
    "__internal" methods, as well as the special "__init__" method, will
    be traced by default.

    If *logger* is unspecified, a default logger will be used to log
    tracing messages.

    """
    logger = keywords.get(
        "logger", logging.getLogger(_generate_logger_name(class_)))

    if method_names:
        traceable_method_names = _get_traceable_method_names(
            method_names, class_)
    else:
        traceable_method_names = _get_default_traceable_method_names(class_)

    # replace each named method with a tracing proxy method
    for method_name in traceable_method_names:
        descriptor = class_.__dict__[method_name]
        descriptor_type = type(descriptor)

        if descriptor_type is FunctionType:
            make_traceable_method = _make_traceable_instancemethod
        elif descriptor_type is classmethod:
            make_traceable_method = _make_traceable_classmethod
        elif descriptor_type is staticmethod:
            make_traceable_method = _make_traceable_staticmethod
        else:
            # should be unreachable, but issue a warning just in case
            warnings.warn("tracing not supported for %r" % descriptor_type)
            continue

        tracing_proxy_descriptor = make_traceable_method(
            class_, descriptor, logger)

        # class_.__dict__ is a mappingproxy; direct assignment not supported
        setattr(class_, method_name, tracing_proxy_descriptor)

    return class_


def _get_traceable_method_names(method_names, class_):
    """Filter (and possibly mangle) *method_names* so that only method
    names actually defined as methods in *cls_dict* remain.

    :param method_names: a sequence of names that should identify
                         methods defined in *class_*
    :param class_: the class being traced
    :return: a sequence of names identifying methods that are defined in
             *class_* that will be traced
    :rtype: list

    .. warning::
       A :exc:`UserWarning` is issued if any method name specified in
       *method_names* is not actually defined in *class_*.

    """
    traceable_method_names = []

    for name in method_names:
        mname = (
            name if not _is_internal_name(name) else
            _mangle_name(name, class_.__name__))

        if isroutine(class_.__dict__.get(mname)):
            traceable_method_names.append(mname)
        else:
            warnings.warn(
                "%r does not identify a method defined in %s" %
                    (name, class_.__name__))

    return traceable_method_names


def _get_default_traceable_method_names(class_):
    """Return all names in *cls_dict* that identify methods.

    :param class_: the class being traced
    :return: a sequence of names identifying methods of *class_* that
             will be traced
    :rtype: list

    """
    default_traceable_method_names = []

    for (name, member) in class_.__dict__.items():
        if isroutine(member) and (
                not _is_special_name(name) or
                name == "__init__"):
            default_traceable_method_names.append(name)

    return default_traceable_method_names


def _is_internal_name(name):
    """Determine whether or not *name* is an "__internal" name.

    :param str name: a name defined in a class ``__dict__``
    :return: ``True`` if *name* is an "__internal" name, else ``False``
    :rtype: bool

    """
    return name.startswith("__") and not name.endswith("__")


def _mangle_name(internal_name, class_name):
    """Transform *name* (which is assumed to be an "__internal" name)
    into a "_ClassName__internal" name.

    :param str internal_name: the assumed-to-be-"__internal" member name
    :param str class_name: the name of the class where *name* is defined
    :return: the transformed "_ClassName__internal" name
    :rtype: str

    """
    return "_%s%s" % (class_name.lstrip('_'), internal_name)


def _is_special_name(name):
    """Determine whether or not *name* is a "__special__" name.

    :param str name: a name defined in a class ``__dict__``
    :return: ``True`` if *name* is a "__special__" name, else ``False``
    :rtype: bool

    """
    return name.startswith("__") and name.endswith("__")


def _make_traceable_instancemethod(class_, method_descriptor, logger):
    """Create a method descriptor that returns the tracing proxy
    function for the instance method described by *method_descriptor*.

    :param class_: the class that owns *method_descriptor*
    :param method_descriptor: the method descriptor of the instance
                              method being traced (i.e. the function)
    :param logging.Logger logger: the logger that will be used for
                                  tracing call and return messages
    :return: a method descriptor that returns the tracing proxy function

    When *logger* is not enabled for the :attr:`autologging.TRACE`
    level, the tracing proxy function will delegate directly to the
    original instance method.

    The original unbound function is available from the proxy
    descriptor's ``__func__.__wrapped__`` attribute.

    """
    # functions have a __get__ method; they can act as descriptors
    function = method_descriptor

    log_delegator = _TracingLoggerDelegator(logger, function)

    @wraps(function)
    def autologging_traced_instancemethod_proxy(f_self, *args, **keywords):
        method = method_descriptor.__get__(f_self, f_self.__class__)
        # don't access from closure (IronPython does not manage
        # co_freevars/__closure__ correctly)
        log_delegator = \
            autologging_traced_instancemethod_proxy._trace_log_delegator
        if log_delegator.isEnabledFor(TRACE):
            log_delegator.trace_call(args, keywords)
            value = method(*args, **keywords)
            log_delegator.trace_return(value)
            return value
        else:
            return method(*args, **keywords)

    # NOT a logging.Logger subclass, but does implement read-only properties
    # and methods that mimic the public logging.Logger interface
    autologging_traced_instancemethod_proxy._trace_log_delegator = \
        log_delegator

    if not hasattr(autologging_traced_instancemethod_proxy, "__wrapped__"):
        # __wrapped__ is only set by functools.wraps() in Python 3.2+
        autologging_traced_instancemethod_proxy.__wrapped__ = function

    autologging_traced_instancemethod_proxy.__autologging_traced__ = True

    return autologging_traced_instancemethod_proxy


def _make_traceable_classmethod(class_, method_descriptor, logger):
    """Create a method descriptor that returns the tracing proxy
    function for the class method described by *method_descriptor*.

    :param class_: the class that owns *method_descriptor*
    :param method_descriptor: the method descriptor of the instance
                              method being traced
    :param logging.Logger logger: the logger that will be used for
                                  tracing call and return messages
    :return: a method descriptor that returns the tracing proxy function

    When *logger* is not enabled for the :attr:`autologging.TRACE`
    level, the tracing proxy function will delegate directly to the
    original class method.

    The original class method is available from the proxy descriptor's
    ``__func__.__wrapped__`` attribute.

    """
    function = method_descriptor.__func__

    log_delegator = _TracingLoggerDelegator(logger, function)

    @wraps(function)
    def autologging_traced_classmethod_proxy(f_cls, *args, **keywords):
        method = method_descriptor.__get__(None, f_cls)
        # don't access from closure (IronPython does not manage
        # co_freevars/__closure__ correctly)
        log_delegator = \
            autologging_traced_classmethod_proxy._trace_log_delegator
        if log_delegator.isEnabledFor(TRACE):
            log_delegator.trace_call(args, keywords)
            value = method(*args, **keywords)
            log_delegator.trace_return(value)
            return value
        else:
            return method(*args, **keywords)

    # NOT a logging.Logger subclass, but does implement read-only properties
    # and methods that mimic the public logging.Logger interface
    autologging_traced_classmethod_proxy._trace_log_delegator = log_delegator

    if not hasattr(autologging_traced_classmethod_proxy, "__wrapped__"):
        # __wrapped__ is only set by functools.wraps() in Python 3.2+
        autologging_traced_classmethod_proxy.__wrapped__ = function

    autologging_traced_classmethod_proxy.__autologging_traced__ = True

    return classmethod(autologging_traced_classmethod_proxy)


def _make_traceable_staticmethod(class_, method_descriptor, logger):
    """Create a method descriptor that returns the tracing proxy
    function for the class method described by *method_descriptor*.

    :param class_: the class that owns *method_descriptor*
    :param method_descriptor: the method descriptor of the instance
                              method being traced
    :param logging.Logger logger: the logger that will be used for
                                  tracing call and return messages
    :return: a method descriptor that returns the tracing proxy function

    When *logger* is not enabled for the :attr:`autologging.TRACE`
    level, the tracing proxy function will delegate directly to the
    original class method.

    The original class method is available from the proxy descriptor's
    ``__func__.__wrapped__`` attribute.

    """
    function = method_descriptor.__func__

    log_delegator = _TracingLoggerDelegator(logger, function)

    @wraps(function)
    def autologging_traced_staticmethod_proxy(*args, **keywords):
        # don't access from closure (IronPython does not manage
        # co_freevars/__closure__ correctly)
        log_delegator = \
            autologging_traced_staticmethod_proxy._trace_log_delegator
        if log_delegator.isEnabledFor(TRACE):
            log_delegator.trace_call(args, keywords)
            value = function(*args, **keywords)
            log_delegator.trace_return(value)
            return value
        else:
            return function(*args, **keywords)

    # NOT a logging.Logger subclass, but does implement read-only properties
    # and methods that mimic the public logging.Logger interface
    autologging_traced_staticmethod_proxy._trace_log_delegator = log_delegator

    if not hasattr(autologging_traced_staticmethod_proxy, "__wrapped__"):
        # __wrapped__ is only set by functools.wraps() in Python 3.2+
        autologging_traced_staticmethod_proxy.__wrapped__ = function

    autologging_traced_staticmethod_proxy.__autologging_traced__ = True

    return staticmethod(autologging_traced_staticmethod_proxy)


class _TracingLoggerDelegator(object):
    """Build CALL/RETURN log records and delegate logging to a specified
    tracing logger.

    """

    @staticmethod
    def _find_last_line_number(f_code):
        """Return the last line number of a function.

        :param types.CodeType f_code: the bytecode object for a
                                      function, as obtained from
                                      ``function.__code__``
        :return: the last physical line number of the function
        :rtype: int

        """
        last_line_number = f_code.co_firstlineno

        # Jython and IronPython do not have co_lnotab
        if hasattr(f_code, "co_lnotab"):
            # co_lnotab is a sequence of 2-byte offsets
            # (address offset, line number offset), each relative to the
            # previous; we only care about the line number offsets here, so
            # start at index 1 and increment by 2
            i = 1
            while i < len(f_code.co_lnotab):
                # co_lnotab is bytes in Python 3, but str in Python 2
                last_line_number += (
                    f_code.co_lnotab[i] if sys.version_info[0] >= 3
                    else ord(f_code.co_lnotab[i]))
                i += 2

        return last_line_number

    def __init__(self, logger, function):
        """
        :param logging.Logger logger: the tracing logger
        :param function: the function being traced
        """
        self._logger = logger

        f_code = function.__code__
        self._f_filename = f_code.co_filename
        self._f_firstlineno = f_code.co_firstlineno
        self._f_lastlineno = self._find_last_line_number(f_code)
        self._f_name = function.__name__

    @property
    def name(self):
        """The name (channel) used by the tracing logger.

        :rtype: str

        """
        return self._logger.name

    @property
    def propagate(self):
        """Whether or not the tracing logger propagates to its parent.

        :rtype: bool

        """
        return self._logger.propagate

    def isEnabledFor(self, level):
        """Whether or not the tracing logger is enabled for *level*.

        :param int level: the logging level being queried
        :rtype: bool

        """
        return self._logger.isEnabledFor(level)

    def getEffectiveLevel(self):
        """Return the effective level for the tracing logger.

        :rtype: int

        """
        return self._logger.getEffectiveLevel()

    def hasHandlers(self):
        """Whether or not any handlers are registered for the tracing
        logger.

        :rtype: bool

        """
        # adapted from Python 3.5 logging module
        c = self._logger
        rv = False
        while c:
            if c.handlers:
                rv = True 
                break
            if not c.propagate:
                break
            else:
                c = c.parent
        return rv

    def trace_call(self, f_args, f_keywords):
        """Emit a CALL log record for the traced function.

        :param tuple f_args: the positional arguments that were passed
                             when the traced function was called
        :param dict f_keywords: the keyword arguments that were passed
                                when the traced function was called

        .. warning::
           This method does **not** perform a level check, and delegates
           *directly* to :meth:`logging.Logger.handle`. The caller is
           expected to perform the level check prior to calling this
           method.

        """
        call_record = logging.LogRecord(
            self._logger.name,      # name
            TRACE,                  # level
            self._f_filename,       # pathname
            self._f_firstlineno,    # lineno
            "CALL *%r **%r",        # msg
            (f_args, f_keywords),   # args
            None,                   # exc_info
            func=self._f_name)
        self._logger.handle(call_record)

    def trace_return(self, f_return):
        """Emit a RETURN log record for the traced function.

        :param f_return: the value returned by the traced function when
                         it was called

        .. warning::
           This method does **not** perform a level check, and delegates
           *directly* to :meth:`logging.Logger.handle`. The caller is
           expected to perform the level check prior to calling this
           method.

        """
        return_record = logging.LogRecord(
            self._logger.name,  # name
            TRACE,              # level
            self._f_filename,   # pathname
            self._f_lastlineno, # lineno
            "RETURN %r",        # msg
            (f_return,),        # args
            None,               # exc_info
            func=self._f_name)
        self._logger.handle(return_record)

