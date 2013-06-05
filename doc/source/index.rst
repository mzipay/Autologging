======================================================
Autologging --- easier logging and tracing for classes
======================================================

:Release: |version|

The :mod:`autologging` module defines two decorators and a metaclass factory
that make :py:mod:`logging` easier to use with classes.

Python 2.7 and Python 3.2+ are supported using the same codebase. All examples
given on this site use Python 3 syntax.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   autologging
   examples

Download and Install
--------------------

* Use "`pip <https://pypi.python.org/pypi/pip>`_ install Autologging".
* Download a source or built distribution from
  `Autologging on SourceForge <http://sourceforge.net/projects/autologging/files/autologging/>`_
  and run either *setup.py* or the binary installer.
* Clone the
  `Autologging Mercurial repository from BitBucket <https://bitbucket.org/mzipay/autologging>`_
  and run *setup.py*.

If you download or clone the source, the test suite can be run from the
project root directory in either of the following ways::

   python -m unittest test.suite
   python setup.py test

Introduction
------------
When using the Python :py:mod:`logging` module to log classes, there are
a couple of challenges that usually must be addressed by the developer:

1. The standard ``logging`` module is not inherently "aware" of classes in the
   context of logging statements made within class methods.
2. The standard ``logging`` module has no concept of tracing (i.e. there are
   neither log methods for tracing nor any log level lower than
   :py:data:`logging.DEBUG` to use for tracing). (See
   `logging vs. tracing <https://www.google.com/search?q=logging+vs.+tracing>`_.)

Challenge #1 is not a failing of the ``logging`` module, but rather a
side-effect of using Python stack frames to determine caller information
(see :py:func:`logging.Logger.findCaller`).

A reasonable workaround for #1 is to simply create a class-level logger that
uses the class's
`qualified name <http://docs.python.org/3/glossary.html#term-qualified-name>`_
as the logger name. This approach is consistent with respect to the ``logging``
module's
`recommended usage <http://docs.python.org/3/library/logging.html#logger-objects>`_
for logger naming (as well as being analogous to *java.util.logging* usage, upon
which Python's ``logging`` module is based).

Challenge #2 can also be worked around, though it requires a bit more effort.
Defining a new log level/name for tracing (via :py:func:`logging.addLevelName`)
is a start, but writing (and maintaining) the tracing log statements becomes
tedious and error prone. In a language as dynamic as Python, it should not be
(and isn't) necessary to do this "by hand."

Class logging boilerplate code belongs in a module
==================================================

As it turns out, the code necessary to create appropriately-named loggers for
classes **and** to trace functions or class methods is boilerplate.

The :mod:`autologging` module encapsulates this boilerplate code for you,
allowing you to use simple decorators and a metaclass to get consistent class
logging and tracing.

A module that employs the use of ``autologging`` resembles the following::

   import logging
   from autologging import logged, traced, TracedMethods

   _logger = logging.getLogger(__name__)


   @traced
   def my_helper():
      _logger.debug("I am doing something helpful.")


   @logged
   class MyClass(metaclass=TracedMethods("my_staticmethod", "my_classmethod",
                                         "my_instancemethod")):

      @staticmethod
      def my_staticmethod():
         MyClass.__logger.debug("I am a static method.")

      @classmethod
      def my_classmethod(cls):
         cls.__logger.debug("I am a class method.")

      def my_instancemethod(self):
         self.__logger.debug("I am an instance method.")

.. versionchanged:: 0.2
   Inner classes and "internal" classes (i.e. classes named with leading
   underscore) are now handled correctly.

A module that uses ``autologging`` for inner classes resembles the following::

   class Outer:

      @logged
      class _Inner:
         """Logger name will be '<modulename>.Outer._Inner'."""

Please see :doc:`autologging` for details, then check out :doc:`examples`.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
