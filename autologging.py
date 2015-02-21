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

__author__ = "Matthew Zipay <mattz@ninthtest.net>, "\
             "Simon Knopp <simon.knopp@pg.canterbury.ac.nz>"
__version__ = "0.4.0"

from functools import wraps
from inspect import isclass, isroutine
import logging
import sys
from types import MethodType
import warnings

__all__ = [
    "logged",
    "TRACE",
    "traced",
    "TracedMethods",
]

_is_py3 = (sys.version_info[0] == 3)

#: A custom tracing log level, lower in severity than :attr:`logging.DEBUG`.
#: Autologging's :func:`traced` and :func:`TracedMethods` create log records
#: with this custom level.
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

    If *obj* is a :obj:`class`, then ``obj.__logger`` will have the
    logger name "module-name.class-name":

    >>> import sys
    >>> logging.basicConfig(
    ...     level=logging.DEBUG, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @logged
    ... class Sample:
    ... 
    ...     def test(self):
    ...         self.__logger.debug("This is a test.")
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

       Under Python 3.3+, ``Nested.__logger`` will have the name
       "autologging.Outer.Nested", while under Python 2.7 or 3.2, the
       logger name will be "autologging.Nested".

    .. versionchanged:: 0.4.0
       Functions decorated with ``@logged`` now use a *single*
       underscore in the logger variable name (e.g.
       ``my_function._logger``) rather than a double underscore.

    If *obj* is a function, then ``obj._logger`` will have the logger
    name "module-name":

    >>> import sys
    >>> logging.basicConfig(
    ...     level=logging.DEBUG, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @logged
    ... def test():
    ...     test._logger.debug("This is a test.")
    ... 
    >>> test()
    DEBUG:autologging:test:This is a test.

    .. note::
       Within a logged function, the ``_logger`` attribute must be
       qualified by the function name.
       
       In the example above, note the call to ``test._logger.debug``.

    If *obj* is a :class:`logging.Logger` object, then that logger is
    used as the parent logger (instead of the default module-named
    logger):

    >>> import sys
    >>> logging.basicConfig(
    ...     level=logging.DEBUG, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> _logger = logging.getLogger("test.parent")
    >>> @logged(_logger)
    ... class Sample:
    ... 
    ...     def test(self):
    ...         self.__logger.debug("This is a test.")
    ... 
    >>> Sample().test()
    DEBUG:test.parent.Sample:test:This is a test.

    Again, functions are similar:

    >>> import sys
    >>> logging.basicConfig(
    ...     level=logging.DEBUG, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> _logger = logging.getLogger("test.parent")
    >>> @logged(_logger)
    ... def test():
    ...     test._logger.debug("This is a test.")
    ... 
    >>> test()
    DEBUG:test.parent:test:This is a test.

    .. note::
       For classes, the logger member is made "private" (i.e.
       ``__logger`` with double underscore) to ensure that log messages
       that include the *%(name)s* format placeholder are written with
       the correct name.

       Consider a subclass of a ``@logged``-decorated parent class. If
       the subclass were **not** decorated with ``@logged`` and could
       access the parent's logger member directly to make logging
       calls, those log messages would display the name of the
       parent class, not the subclass. 

       Therefore, subclasses of a ``@logged``-decorated parent class
       that wish to use a provided ``self.__logger`` object must
       themselves be decorated with ``@logged``.

    .. warning::
       Although the ``@logged`` and ``@traced`` decorators will "do the
       right thing" regardless of the order in which they are applied to
       the same function, it is recommended that ``@logged`` always be
       used as the innermost decorator::

          @traced
          @logged
          def my_function():
              my_function._logger.info("message")

       This is because ``@logged`` simply sets the ``_logger`` attribute
       and then returns the original function, making it "safe" to use
       in combination with any other decorator.

    """
    if (isinstance(obj, logging.Logger)):
        # decorated as `@logged(logger)' - use logger as parent
        return lambda class_or_fn: _add_logger_to(class_or_fn, obj.name)
    else:
        # decorated as `@logged' - use module logger as parent
        return _add_logger_to(obj, obj.__module__)


def _add_logger_to(obj, parent_name):
    """Set ``obj.__logger`` as a :class:`logging.Logger` whose parent
    logger is named by *parent_name*.

    :param obj: a class or function object
    :return: *obj*

    """
    if (isclass(obj)):
        class_name = getattr(obj, "__qualname__", obj.__name__)
        logger = logging.getLogger("%s.%s" % (parent_name, class_name))
        setattr(obj, _mangle("__logger", obj.__name__), logger)
    else:   # function
        # use parent logger name directly - the function name is available as
        # the %(funcName)s var in a logging.Formatter, and so is redundant to
        # include in the logger name
        obj._logger = logging.getLogger(parent_name)
    return obj


def traced(obj):
    """Add call and return tracing to an unbound function.

    :param obj: the function object being decorated, or an optional
                :class:`logging.Logger` object to be used as the parent
                logger (instead of the default module-named logger)
    :return: if *obj* is a function, returns a proxy function that
             wraps *obj* to provide the call and return tracing;
             otherwise, if *obj* is a logger, returns another function
             decorator that creates and returns the tracing proxy
             function

    .. note::
       The original (proxied) function is available as the
       ``__wrapped__`` attribute of the returned proxy function. For
       example:

       >>> import sys
       >>> logging.basicConfig(
       ...     level=TRACE, stream=sys.stdout,
       ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
       >>> @traced
       ... def my_function(arg):
       ...     return arg.upper()
       ... 
       >>> my_function.__wrapped__("test")
       'TEST'

       (Note that the tracing log records were not written because the
       *original, non-traced* function was called.)

    .. warning::
       This decorator will not quite work as expected (or may fail
       entirely) for class methods. To automatically trace class
       method call/return, please see the :class:`TracedMethods`
       metaclass factory.

    In the following example, tracing log messages are written to a
    log whose name defaults to the function's module name:

    >>> import sys
    >>> logging.basicConfig(
    ...     level=TRACE, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> @traced
    ... def my_function(arg, keyword=None):
    ...     return "%s and %s" % (arg, keyword)
    ... 
    >>> my_function("spam", keyword="eggs")
    TRACE:autologging:my_function:CALL *('spam',) **{'keyword': 'eggs'}
    TRACE:autologging:my_function:RETURN 'spam and eggs'
    'spam and eggs'

    In the following example, tracing log messages are written to
    a user-named log:

    >>> import sys
    >>> logging.basicConfig(
    ...     level=TRACE, stream=sys.stdout,
    ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
    >>> _logger = logging.getLogger("test.ing")
    >>> @traced(_logger)
    ... def my_function(arg, keyword=None):
    ...     return "%s and %s" % (arg, keyword)
    ... 
    >>> my_function("spam", keyword="eggs")
    TRACE:test.ing:my_function:CALL *('spam',) **{'keyword': 'eggs'}
    TRACE:test.ing:my_function:RETURN 'spam and eggs'
    'spam and eggs'

    .. warning::
       Although the ``@traced`` and ``@logged`` decorators will "do the
       right thing" regardless of the order in which they are applied to
       the same function, it is recommended that ``@logged`` always be
       used as the innermost decorator::

          @traced
          @logged
          def my_function():
              my_function._logger.info("message")

       This is because ``@logged`` simply sets the ``_logger`` attribute
       and then returns the original function, making it "safe" to use
       in combination with any other decorator.

    """
    if (isinstance(obj, logging.Logger)):
        # decorated as `@traced(logger)' - log to logger
        def traced_decorator(function):
            return _make_function_tracer(function, obj)
        return traced_decorator
    else:   # function
        # decorated as `@traced' - log to module logger
        logger = logging.getLogger(obj.__module__)
        return _make_function_tracer(obj, logger)


def _make_function_tracer(function, logger):
    """Return a tracing proxy function for *function*.

    :param function: an unbound, module-level (or nested) function
    :param logging.Logger logger: the logger to use for tracing messages
    :return: a proxy function that wraps *function* to provide the call
             and return tracing

    """
    logger_delegator = _TracingLoggerDelegator(logger, function)
    @wraps(function)
    def autologging_traced_function_proxy(*args, **keywords):
        if (logger_delegator.isEnabledFor(TRACE)):
            logger_delegator.log_call(args, keywords)
            return_value = function(*args, **keywords)
            logger_delegator.log_return(return_value)
            return return_value
        else:
            return function(*args, **keywords)
    if (not hasattr(autologging_traced_function_proxy, "__wrapped__")):
        # __wrapped__ is only set by functools.wraps() in Python 3.2+
        autologging_traced_function_proxy.__wrapped__ = function
    autologging_traced_function_proxy.__autologging_proxy__ = True
    return autologging_traced_function_proxy


# can't use option=<default> keywords with *args in Python 2.7 (see PEP-3102)
def TracedMethods(*args, **options):
    """Return a metaclass that provides call and return tracing for a
    class's methods.

    The contents of *args* and *options* determine which methods will be
    traced, and which logger will be used for tracing messages:

    TracedMethods()
       In the simplest configuration, all "public", "_nonpublic", and
       "__private" methods that are defined *in the class body* (as well
       as the special ``__init__`` method, if defined) will be traced.
       The class ``__dict__`` will be inspected to identify these
       methods and replace them with tracing proxy methods. (Inherited
       methods are **never** traced. See the note below.)
       Tracing messages will be logged to the "module-name.class-name"
       logger at the :attr:`autologging.TRACE` level.

       Example:

       >>> import sys
       >>> logging.basicConfig(
       ...     level=TRACE, stream=sys.stdout,
       ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
       >>> class Sample(metaclass=TracedMethods()):
       ...     @staticmethod
       ...     def static_method():
       ...         return "STATIC"
       ...     @classmethod
       ...     def class_method(cls):
       ...         return "CLASS"
       ...     def __init__(self):
       ...         self.public = "PUBLIC"
       ...     def method(self, arg, kw=None):
       ...         return "%s%s" % (self.public if kw is None else kw,
       ...                          arg)
       ...     def _nonpublic(self):
       ...         return "NON_PUBLIC"
       ...     def __private(self):
       ...         return "PRIVATE"
       ...     def __eq__(self, other):
       ...         return False
       ... 
       >>> Sample.static_method()
       TRACE:autologging.Sample:static_method:CALL *() **{}
       TRACE:autologging.Sample:static_method:RETURN 'STATIC'
       'STATIC'
       >>> Sample.class_method()
       TRACE:autologging.Sample:class_method:CALL *() **{}
       TRACE:autologging.Sample:class_method:RETURN 'CLASS'
       'CLASS'
       >>> sample = Sample()
       TRACE:autologging.Sample:__init__:CALL *() **{}
       TRACE:autologging.Sample:__init__:RETURN None
       >>> sample.method(1)
       TRACE:autologging.Sample:method:CALL *(1,) **{}
       TRACE:autologging.Sample:method:RETURN 'PUBLIC1'
       'PUBLIC1'
       >>> sample.method(2, kw="METHOD")
       TRACE:autologging.Sample:method:CALL *(2,) **{'kw': 'METHOD'}
       TRACE:autologging.Sample:method:RETURN 'METHOD2'
       'METHOD2'
       >>> sample._nonpublic()
       TRACE:autologging.Sample:_nonpublic:CALL *() **{}
       TRACE:autologging.Sample:_nonpublic:RETURN 'NON_PUBLIC'
       'NON_PUBLIC'
       >>> sample._Sample__private()
       TRACE:autologging.Sample:__private:CALL *() **{}
       TRACE:autologging.Sample:__private:RETURN 'PRIVATE'
       'PRIVATE'
       >>> sample == 79  # calls __eq__ (not traced by default)
       False

    TracedMethods(logger)
       In this configuration, ``args[0]`` is a :class:`logging.Logger`
       object. This configuration is identical to ``TracedMethods()``,
       except that tracing messages will be logged to the
       "logger-name.class-name" logger.

       Example:

       >>> import sys
       >>> logging.basicConfig(
       ...     level=TRACE, stream=sys.stdout,
       ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
       >>> _logger = logging.getLogger("my.named.logger")
       >>> class Sample(metaclass=TracedMethods(_logger)):
       ...     def method(self):
       ...         return "METHOD"
       ... 
       >>> sample = Sample()  # inherited __init__ is not traced
       >>> sample.method()
       TRACE:my.named.logger.Sample:method:CALL *() **{}
       TRACE:my.named.logger.Sample:method:RETURN 'METHOD'
       'METHOD'

    TracedMethods("method_1", ... , "method_N")
       In this configuration, only the explicitly-named methods will be
       traced.

       Example:

       >>> import sys
       >>> logging.basicConfig(
       ...     level=TRACE, stream=sys.stdout,
       ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
       >>> class Sample(metaclass=TracedMethods("test", "_calc")):
       ...     def __init__(self, multiplicand):
       ...         self._multiplicand = multiplicand
       ...     def test(self, multiplier):
       ...         return "%.2f" % self._calc(abs(multiplier))
       ...     def _calc(self, multiplier):
       ...         return multiplier * self._multiplicand
       ... 
       >>> sample = Sample(7)  # __init__ is not named, so not traced
       >>> sample.test(-9)
       TRACE:autologging.Sample:test:CALL *(-9,) **{}
       TRACE:autologging.Sample:_calc:CALL *(9,) **{}
       TRACE:autologging.Sample:_calc:RETURN 63
       TRACE:autologging.Sample:test:RETURN '63.00'
       '63.00'

    TracedMethods(logger, "method_1", ... , "method_N")
       This configuration is identical to
       ``TracedMethods("method_1", ... , "method_N")``, except that
       tracing messages will be logged to the "logger-name.class-name"
       logger.

       Example:

       >>> import sys
       >>> logging.basicConfig(
       ...     level=TRACE, stream=sys.stdout,
       ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
       >>> _logger = logging.getLogger("my.named.logger")
       >>> class Sample(
       ...         metaclass=TracedMethods(_logger, "test", "_calc")):
       ...     def __init__(self, multiplicand):
       ...         self._multiplicand = multiplicand
       ...     def test(self, multiplier):
       ...         return "%.2f" % self._calc(abs(multiplier))
       ...     def _calc(self, multiplier):
       ...         return multiplier * self._multiplicand
       ... 
       >>> sample = Sample(7)  # __init__ is not named, so not traced
       >>> sample.test(-9)
       TRACE:my.named.logger.Sample:test:CALL *(-9,) **{}
       TRACE:my.named.logger.Sample:_calc:CALL *(9,) **{}
       TRACE:my.named.logger.Sample:_calc:RETURN 63
       TRACE:my.named.logger.Sample:test:RETURN '63.00'
       '63.00'

    TracedMethods(trace_special_methods=True)
       This configuration is identical to ``TracedMethods()``, except
       that "__special__" methods (e.g. ``__eq__``, ``__iter__``, etc.)
       will also be traced.

       Example:

       >>> import sys
       >>> logging.basicConfig(
       ...     level=TRACE, stream=sys.stdout,
       ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
       >>> class Sample(
       ...         metaclass=TracedMethods(trace_special_methods=True)):
       ...     def method(self):
       ...         return "METHOD"
       ...     def __eq__(self, other):
       ...         return False
       ... 
       >>> sample = Sample()  # inherited __init__ is not traced
       >>> sample.method()
       TRACE:autologging.Sample:method:CALL *() **{}
       TRACE:autologging.Sample:method:RETURN 'METHOD'
       'METHOD'
       >>> sample == 79  # calls __eq__
       TRACE:autologging.Sample:__eq__:CALL *(79,) **{}
       TRACE:autologging.Sample:__eq__:RETURN False
       False

       .. note::
          The ``trace_special_methods`` option is **ignored** when
          methods are named explicitly in *args*.

    TracedMethods(logger, trace_special_methods=True)
       This configuration is identical to
       ``TracedMethods(trace_special_methods=True)``, except that
       tracing messages are logged to the "logger-name.class-name"
       logger.

       Example:

       >>> import sys
       >>> logging.basicConfig(
       ...     level=TRACE, stream=sys.stdout,
       ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
       >>> _logger = logging.getLogger("my.named.logger")
       >>> class Sample(
       ...         metaclass=TracedMethods(_logger,
       ...                                 trace_special_methods=True)):
       ...     def method(self):
       ...         return "METHOD"
       ...     def __eq__(self, other):
       ...         return False
       ... 
       >>> sample = Sample()  # inherited __init__ is not traced
       >>> sample.method()
       TRACE:my.named.logger.Sample:method:CALL *() **{}
       TRACE:my.named.logger.Sample:method:RETURN 'METHOD'
       'METHOD'
       >>> sample == 79  # calls __eq__
       TRACE:my.named.logger.Sample:__eq__:CALL *(79,) **{}
       TRACE:my.named.logger.Sample:__eq__:RETURN False
       False

    .. warning::
       Inherited methods are **never** traced, even if they are named
       explicitly in *args*.

       If you wish to trace a method from a super class, you have two
       options:

       1. Use ``TracedMethods`` in the super class.
       2. Override the method in the subclass and trace it there. For
          example::

             class SubClass(SuperClass,
                            metaclass=TracedMethods("method_name")):
                 ...
                 def method_name(self):
                     return super().method_name()
                 ...

    .. warning::
       When method names are specified explicitly via *args*,
       Autologging ensures that each method is actually defined **in
       the body of the class being traced**.

       If a defintion for any named method is not found in the class
       body, either because the method is inherited or because the
       name is misspelled, Autologging will issue a :exc:`UserWarning`.

    .. note::
       Regardless of whether a logger was explicitly passed in or not,
       the logger used by tracing methods is **not** available to the
       class or its instances.

    .. note::
       A class may be decorated by :func:`logged` **and** use
       ``TracedMethods`` as a metaclass without conflict.

    """
    trace_special_methods = options.get("trace_special_methods", False)

    def make_traced_class(cls_name, cls_bases, cls_dict):
        # it is necessary to build the metaclass itself dynamically in order to
        # support the use of TracedMethods in subclasses; otherwise we'd get a
        # metaclass conflict since a subclass's metaclass must itself be a
        # subclass of EACH parent class's metaclass
        meta_bases = []
        for cls_base in cls_bases:
            meta_base = type(cls_base)
            if ((meta_base not in meta_bases) and (meta_base is not type)):
                meta_bases.append(meta_base)
        meta_bases.append(type)

        def traced_meta_new(type_, name, bases, dict_):
            # do not install the tracer proxies if any of the parent class's
            # metaclass is the same as THIS metaclass - this occurs when a
            # parent class is traced but a subclass is not, and in this
            # scenario we choose to NOT trace the child class (i.e. "Explicit
            # is better than implicit.")
            if (type_ not in [type(base) for base in bases]):
                qualname = dict_.get("__qualname__", name)
                if (args and isinstance(args[0], logging.Logger)):
                    logger = logging.getLogger("%s.%s" %
                                               (args[0].name, qualname))
                    method_names = args[1:]
                else:
                    logger = logging.getLogger("%s.%s" %
                                               (dict_["__module__"], qualname))
                    method_names = args

                if (method_names):
                    # caller provided method names; make sure they are
                    # explicitly defined, and mangle any "__method" names
                    method_names = _get_traceable_method_names(method_names,
                                                               name, dict_)
                else:
                    # caller did NOT provide method names; use defaults
                    method_names = _get_default_traceable_method_names(
                            dict_,
                            include_special_methods=trace_special_methods)

                # replace each named method with a tracing proxy method
                for method_name in method_names:
                    descriptor = dict_[method_name]
                    descriptor_type = type(descriptor)
                    if (descriptor_type is staticmethod):
                        tracing_proxy = _make_staticmethod_tracer(descriptor,
                                                                  logger)
                    elif (descriptor_type is classmethod):
                        tracing_proxy = _make_classmethod_tracer(descriptor,
                                                                 logger)
                    else:
                        tracing_proxy = _make_instancemethod_tracer(descriptor,
                                                                    logger)
                    dict_[method_name] = tracing_proxy
            # do not use super(Traced, type_) here! we do not want __new__
            # called more than once (otherwise we'd see autologging proxy
            # descriptors in the new class __dict__ and errors would ensue)
            return type.__new__(type_, name, bases, dict_)

        # this bit of trickery is necessary for Python 2/3 compatibility:
        # Py3 accepts 'class Name(*meta_bases):` but Py2 does not
        Traced = type.__new__(type, "Traced", tuple(meta_bases),
                              {"__new__": traced_meta_new})
        return Traced.__new__(Traced, cls_name, cls_bases, cls_dict)

    return make_traced_class


def _get_traceable_method_names(method_names, cls_name, cls_dict):
    """Filter (and possibly mangle) *method_names* so that only method
    names actually defined as methods in *cls_dict* remain.

    :param method_names: a sequence of names that should identify methods
                         defined in *cls_dict*
    :param str cls_name: the name of the class whose ``__dict__` is
                         *cls_dict*
    :param dict cls_dict: the class ``__dict__`` of the class named by
                          *cls_name*
    :return: a sequence of names identifying methods that are defined in
             *cls_dict*
    :rtype: list

    """
    traceable_method_names = []
    for name in method_names:
        mname = name if (not _is_private(name)) else _mangle(name, cls_name)
        if (isroutine(cls_dict.get(mname))):
            traceable_method_names.append(mname)
        else:
            warnings.warn("%r does not identify a method defined in %s" %
                            (name, cls_name),
                          # issue warning from TracedMethods
                          stacklevel=4)
    return traceable_method_names


def _get_default_traceable_method_names(cls_dict,
                                        include_special_methods=False):
    """Return all names in *cls_dict* that identify methods.

    :param dict cls_dict: the class ``__dict__`` of a class being traced
    :keyword bool include_special_methods:
       if ``True``, then "__special__" methods will be included in the
       returned list
    :return: a sequence of names identifying methods that are defined in
             *cls_dict*
    :rtype: list

    """
    default_traceable_method_names = []
    for name in cls_dict:
        # this check is necessary for Python 2.7 because we set __metaclass__
        # as the make_traced_class function
        if (name == "__metaclass__"):
            continue
        if (isroutine(cls_dict[name]) and
                ((not _is_special(name)) or
                 (include_special_methods or (name == "__init__")))):
            default_traceable_method_names.append(name)
    return default_traceable_method_names


def _is_private(name):
    """Determine whether or *name* is a "__private" name.

    :param str name: a name defined in a class ``__dict__``
    :return: ``True`` if *name* is a "__private" name, else ``False``
    :rtype: bool

    """
    return (name.startswith("__") and (not name.endswith("__")))


def _mangle(name, class_name):
    """Transform *name* (which is assumed to be a "__private" name) into
    a class-internal "_ClassName__mangled" name.

    :param str name: the assumed-to-be-"__private" member name
    :param str class_name: the name of the class where *name* is defined
    :return: the transformed "_ClassName__mangled" name
    :rtype: str

    """
    return "_%s%s" % (class_name.lstrip('_'), name)


def _is_special(name):
    """Determine whether or not *name* if a "__special__" name.

    :param str name: a name defined in a class ``__dict__``
    :return: ``True`` if *name* is a "__special__" name, else ``False``
    :rtype: bool

    """
    return (name.startswith("__") and name.endswith("__"))


class AutologgingProxyDescriptor(object):
    """The super class of all tracing proxy function descriptors.

    This is a "convenience" class that makes introspection of traced
    classes easier. Given a class ``C``, the following iterator yields
    all methods that have been traced::

       for (name, value) in C.__dict__.items():
           if (isinstance(value, AutologgingProxyDescriptor)):
               yield value.__func__

    """


def _make_instancemethod_tracer(function, logger):
    """Return a tracing proxy method descriptor for the instance method
    *function*.

    :param function: the instance method being traced
    :param logging.Logger logger: the logger that will be used for
                                  tracing call and return messages
    :return: a method descriptor that returns the tracing proxy function

    When *logger* is not enabled for the :attr:`autologging.TRACE`
    level, the tracing proxy function will delegate directly to
    *function*.

    .. note::
       The original (non-traced) *function* is available from either the
       descriptor's ``__func__`` attribute or the the tracing proxy
       function's ``__wrapped__`` attribute.

    """
    logger_delegator = _TracingLoggerDelegator(logger, function)

    @wraps(function)
    def autologging_traced_instancemethod_proxy(self, *args, **keywords):
        method = function.__get__(self, self.__class__)
        if (logger_delegator.isEnabledFor(TRACE)):
            logger_delegator.log_call(args, keywords)
            return_value = method(*args, **keywords)
            logger_delegator.log_return(return_value)
            return return_value
        else:
            return method(*args, **keywords)
    if (not hasattr(autologging_traced_instancemethod_proxy, "__wrapped__")):
        # __wrapped__ is only set by functools.wraps() in Python 3.2+
        autologging_traced_instancemethod_proxy.__wrapped__ = function
    autologging_traced_instancemethod_proxy.__autologging_proxy__ = True

    class AutologgingInstanceMethodProxyDescriptor(AutologgingProxyDescriptor):
        __func__ = function
        def __get__(self, obj, obj_type=None):
            if (obj is not None):
                return (
                    MethodType(autologging_traced_instancemethod_proxy, obj)
                    if _is_py3 else
                    MethodType(autologging_traced_instancemethod_proxy, obj,
                               obj_type if (obj_type is not None)
                                        else obj.__class__)
                )
            elif (obj_type is not None):
                return (
                    autologging_traced_instancemethod_proxy if _is_py3
                    else MethodType(autologging_traced_instancemethod_proxy,
                                    None, obj_type)
                )
            else:
                raise TypeError("__get__(None, None) is invalid")

    return AutologgingInstanceMethodProxyDescriptor()


def _make_classmethod_tracer(descriptor, logger):
    """Return a tracing proxy method descriptor for the class method
    accessed via *descriptor*.

    :param descriptor: the method descriptor for the class method being
                       traced
    :param logging.Logger logger: the logger that will be used for
                                  tracing call and return messages
    :return: a method descriptor that returns the tracing proxy function

    When *logger* is not enabled for the :attr:`autologging.TRACE`
    level, the tracing proxy function will delegate directly to
    *function*.

    .. note::
       The original (non-traced) function is available from either the
       descriptor's ``__func__`` attribute or the the tracing proxy
       function's ``__wrapped__`` attribute.

    """
    function = descriptor.__func__
    logger_delegator = _TracingLoggerDelegator(logger, function)

    @wraps(function)
    def autologging_traced_classmethod_proxy(cls, *args, **keywords):
        method = descriptor.__get__(None, cls)
        if (logger_delegator.isEnabledFor(TRACE)):
            logger_delegator.log_call(args, keywords)
            return_value = method(*args, **keywords)
            logger_delegator.log_return(return_value)
            return return_value
        else:
            return method(*args, **keywords)
    if (not hasattr(autologging_traced_classmethod_proxy, "__wrapped__")):
        # __wrapped__ is only set by functools.wraps() in Python 3.2+
        autologging_traced_classmethod_proxy.__wrapped__ = function
    autologging_traced_classmethod_proxy.__autologging_proxy__ = True

    class AutologgingClassMethodProxyDescriptor(AutologgingProxyDescriptor):
        __func__ = function
        def __get__(self, obj, obj_type=None):
            if (obj_type is not None):
                return MethodType(autologging_traced_classmethod_proxy,
                                  obj_type)
            elif (obj is not None):
                return MethodType(autologging_traced_classmethod_proxy,
                                  obj.__class__)
            else:
                raise TypeError("__get__(None, None) is invalid")

    return AutologgingClassMethodProxyDescriptor()


def _make_staticmethod_tracer(descriptor, logger):
    """Return a tracing proxy method descriptor for the static method
    accessed via *descriptor*.

    :param descriptor: the method descriptor for the static method being
                       traced
    :param logging.Logger logger: the logger that will be used for
                                  tracing call and return messages
    :return: a method descriptor that returns the tracing proxy function

    When *logger* is not enabled for the :attr:`autologging.TRACE`
    level, the tracing proxy function will delegate directly to
    *function*.

    .. note::
       The original (non-traced) function is available from either the
       descriptor's ``__func__`` attribute or the the tracing proxy
       function's ``__wrapped__`` attribute.

    """
    function = descriptor.__func__
    logger_delegator = _TracingLoggerDelegator(logger, function)

    @wraps(function)
    def autologging_traced_staticmethod_proxy(*args, **keywords):
        method = descriptor.__get__(object)
        if (logger_delegator.isEnabledFor(TRACE)):
            logger_delegator.log_call(args, keywords)
            return_value = method(*args, **keywords)
            logger_delegator.log_return(return_value)
            return return_value
        else:
            return method(*args, **keywords)
    if (not hasattr(autologging_traced_staticmethod_proxy, "__wrapped__")):
        # __wrapped__ is only set by functools.wraps() in Python 3.2+
        autologging_traced_staticmethod_proxy.__wrapped__ = function
    autologging_traced_staticmethod_proxy.__autologging_proxy__ = True

    class AutologgingStaticMethodProxyDescriptor(AutologgingProxyDescriptor):
        __func__ = function
        def __get__(self, obj, obj_type=None):
            if ((obj is not None) or (obj_type is not None)):
                return autologging_traced_staticmethod_proxy
            else:
                raise TypeError("__get__(None, None) is invalid")

    return AutologgingStaticMethodProxyDescriptor()


class _TracingLoggerDelegator(object):
    """A :class:`logging.Logger` delegator class that adds tracing
    capabilities.

    .. warning::
       This class does **not** expose the full interface of the
       underlying :class:`logging.Logger`. Only fields and methods that
       are necessary to support tracing are exposed.

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
        # co_lnotab is a sequence of 2-byte offsets (address offset, line number
        # offset), each relative to the previous; we only care about the line
        # number offsets here, so start at index 1 and increment by 2
        i = 1
        while (i < len(f_code.co_lnotab)):
            # co_lnotab is bytes in Python 3, but str in Python 2
            last_line_number += (f_code.co_lnotab[i] if _is_py3
                                 else ord(f_code.co_lnotab[i]))
            i += 2
        return last_line_number

    def __init__(self, delegate_logger, proxied_function):
        """
        :param logging.Logger delegate_logger:
           the logger that will actually handle tracing call and return
           log records
        :param proxied_function: the function being traced

        Caller information (function name, source file name, and
        first/last line number) is extracted from *proxied_function* to
        be used when creating :class:`logging.LogRecord` objects for
        tracing call and return messages.

        """
        self._logger = delegate_logger
        self._caller_name = proxied_function.__name__
        f_code = proxied_function.__code__
        self._caller_filename = f_code.co_filename
        self._caller_firstlineno = f_code.co_firstlineno
        self._caller_lastlineno = self._find_last_line_number(f_code)

    @property
    def name(self):
        """The name of the delegate :class:`logging.Logger`."""
        return self._logger.name

    @property
    def level(self):
        """The level (:obj:`int`) of the delegate
        :class:`logging.Logger`.

        """
        return self._logger.level

    @property
    def parent(self):
        """The parent logger of the delegate :class:`logging.Logger`."""
        return self._logger.parent

    def getEffectiveLevel(self):
        """Return The **effecive** level of the delegate
        :class:`logging.Logger`.

        """
        return self._logger.getEffectiveLevel()

    def isEnabledFor(self, level):
        """Is the delegate :class:`logging.Logger` enabled for *level*?"""
        return self._logger.isEnabledFor(level)

    def log_call(self, f_args, f_keywords):
        """Send a message indicating that the proxied function has been
        called.

        :param tuple f_args: the positional arguments that were sent to
                             the proxied function
        :param dict f_keywords: the keyword arguments that were sent to
                                the proxied function

        """
        record = logging.LogRecord(self._logger.name, TRACE,
                                   self._caller_filename,
                                   self._caller_firstlineno, "CALL *%r **%r",
                                   (f_args, f_keywords), None,
                                   func=self._caller_name)
        self._logger.handle(record)

    def log_return(self, f_return_value):
        """Send a message indicating that the proxied function has
        returned.

        :param f_return_value: the value that was returned by the
                               proxied function

        """
        record = logging.LogRecord(self._logger.name, TRACE,
                                   self._caller_filename,
                                   self._caller_lastlineno, "RETURN %r",
                                   (f_return_value,), None,
                                   func=self._caller_name)
        self._logger.handle(record)

