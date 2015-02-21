===========================
Introduction to Autologging
===========================

:Release: |release|

When using the Python :mod:`logging` module to log classes, there are a couple
of challenges that usually must be addressed by the developer:

1. The standard ``logging`` module is not inherently "aware" of classes in the
   context of logging statements made within class methods.
2. The standard ``logging`` module has no concept of tracing (i.e. there are
   neither log methods for tracing nor any log levels lower than
   :attr:`logging.DEBUG` to use for tracing). (See
   `logging vs. tracing <https://www.google.com/search?q=logging+vs.+tracing>`_.)

Challenge #1 is not a failing of the ``logging`` module, but rather a
side-effect of using Python stack frames to determine caller information
(see :meth:`logging.Logger.findCaller`).

A reasonable workaround for #1 is to simply create a class-level logger that
uses the class's `qualified name
<http://docs.python.org/3/glossary.html#term-qualified-name>`_ as the logger
name. This approach is consistent with respect to the ``logging`` module's
`recommended usage
<http://docs.python.org/3/library/logging.html#logger-objects>`_ for logger
naming (as well as being analogous to `java.util.logging
<http://docs.oracle.com/javase/8/docs/api/java/util/logging/package-summary.html>`_
and `log4j <http://logging.apache.org/log4j/2.x/>`_ usage, upon which Python's
``logging`` module is based).

Challenge #2 can also be worked around, though it requires a bit more effort.
Defining a new log level/name for tracing (via :func:`logging.addLevelName`) is
a start, but writing (and maintaining) the tracing log statements becomes
tedious and error prone. In a language as dynamic as Python, it should not be
(and isn't) necessary to do this "by hand."

As it turns out, the code necessary to create appropriately-named loggers for
classes **and** to trace functions or class methods is boilerplate.

The :mod:`autologging` module encapsulates this boilerplate code for you,
allowing you to use simple decorators and a metaclass to get consistent class
logging and tracing.

Logging and tracing "by hand"
-----------------------------

::

   # my_module.py

   import logging

   logging.addLevelName(1, "TRACE")


   class MyClass:

      __logger = logging.getLogger("%s.MyClass" % __name__)

      def my_method(self, arg, keyword=None):
         self.__logger.log(TRACE, "CALL %r keyword=%r", arg, keyword)
         self.__logger.info("my message")
         phrase = "%s and %s" % (arg, keyword)
         self.__logger.log(TRACE, "RETURN %r", phrase)
         return phrase

Assuming we've already configured logging to use the format
*"%(levelname)s:%(name)s:%(funcName)s:%(message)s"*, calling "my_method"
produces the following log output::

   TRACE:my_module.MyClass:my_method:CALL 'spam' keyword='eggs'
   INFO:my_module.MyClass:my_method:my message
   TRACE:my_module.MyClass:my_method:RETURN 'spam and eggs'

Using this approach, we end up with several lines of visual clutter:

* The purpose of "my_method" is to join the arg and keyword together into a
  phrase, but there are more lines dedicated to logging/tracing than to the
  method logic.
* Because we wish to trace the return value of the method, we **must** set the
  return value as an intermediate local variable so that it can be traced, then
  returned.
  This means we can't simply use the much more succinct expression
  ``return "%s and %s" % (arg, keyword)``.

Aside from visual clutter, there are maintenance issues as well:

* If the name of the class changes, the logger name must be updated manually.
* If anything about the method signature changes (number and/or position of
  arguments, number and/or names of keyword arguments), then the "CALL" tracing
  log statement must be updated manually.
* If "my_method" were ever refactored to, say, return with a different value if
  keyword is ``None``, then we'd need to either add *another* logging statement
  to trace the early return, or we'd need to reconstruct the method body to set
  ``phrase`` accordingly before tracing and returning.

Logging and tracing with ``autologging``
----------------------------------------

Autologging addresses **all** of the issues in the previous sample, resulting
in less code that's more readable and easier to maintain::

   # my_module.py

   from autologging import logged, TracedMethods

   @logged
   class MyClass(metaclass=TracedMethods()):

      def def my_method(self, arg, keyword=None):
         self.__logger.info("my message")
         return "%s and %s" % (arg, keyword)

Assuming we've already configured logging to use the format
*"%(levelname)s:%(name)s:%(funcName)s:%(message)s"*, calling "my_method"
produces the following log output::

   TRACE:my_module.MyClass:my_method:CALL *('spam',) **{'keyword': 'eggs'}
   INFO:my_module.MyClass:my_method:my message
   TRACE:my_module.MyClass:my_method:RETURN 'spam and eggs'

Please see :doc:`autologging` for details, then check out :doc:`examples`.

