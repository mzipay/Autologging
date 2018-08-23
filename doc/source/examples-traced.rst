===============================
Using the ``@traced`` decorator
===============================

:Release: |release|

* :ref:`module-traced-class`
* :ref:`named-traced-class`
* :ref:`specific-traced-methods`
* :ref:`traced-generators`
* :ref:`traced-nested-class`
* :ref:`module-traced-function`
* :ref:`named-traced-function`
* :ref:`traced-nested-function`

.. warning::
   The ``@traced`` decorator will not work as you might expect when it
   decorates a function (method) in the body of a class. In general,
   prefer to decorate the class itself, explicitly identifying the
   method names to trace if the default (all class, static, and instance
   methods, excluding "__special__" methods, with the exception of
   ``__init__`` and ``__call__``) doesn't suit your needs.

.. _module-traced-class:

Trace all methods of a class using a module-named logger
========================================================

This is the simplest way to use the :func:`autologging.traced`
decorator. All *non-special* methods of the class are traced to a logger
that is named after the containing module and class. (Note: the special
``__init__`` method is an exception to the rule - it is traced by
default if it is defined.)

.. note::
   Inherited methods are **never** traced. If you want tracing for
   inherited methods, either trace them in the super class, or override
   and trace them in the subclass.

::

   # my_module.py

   from autologging import traced


   @traced
   class MyClass:

      def __init__(self):
         self._value = "ham"

      def my_method(self, arg, keyword=None):
         return "%s, %s, and %s" % (arg, self._value, keyword)

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import MyClass
   >>> my_obj = MyClass()
   TRACE:my_module.MyClass:__init__:CALL *() **{}
   TRACE:my_module.MyClass:__init__:RETURN None
   >>> my_obj.my_method("spam", keyword="eggs")
   TRACE:my_module.MyClass:my_method:CALL *('spam',) **{'keyword': 'eggs'}
   TRACE:my_module.MyClass:my_method:RETURN 'spam, ham, and eggs'
   'spam, ham, and eggs'

.. _named-traced-class:

Trace all methods of a class using a user-named logger
======================================================

This example is identical to the above example, except that the tracing
logger has a user-defined name ("tracing.example" in this case). Simply
pass the user-defined logger as the first positional argument to
``traced``::

   # my_module.py

   import logging
   from autologging import traced


   @traced(logging.getLogger("tracing.example"))
   class MyClass:

      def __init__(self):
         self._value = "ham"

      def my_method(self, arg, keyword=None):
         return "%s, %s, and %s" % (arg, self._value, keyword)

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import MyClass
   >>> my_obj = MyClass()
   TRACE:tracing.example.MyClass:__init__:CALL *() **{}
   TRACE:tracing.example.MyClass:__init__:RETURN None
   >>> my_obj.my_method("spam", keyword="eggs")
   TRACE:tracing.example.MyClass:my_method:CALL *('spam',) **{'keyword': 'eggs'}
   TRACE:tracing.example.MyClass:my_method:RETURN 'spam, ham, and eggs'
   'spam, ham, and eggs'

.. _specific-traced-methods:

Trace only certain methods of a class
=====================================

The ``traced`` decorator accepts a variable number of positional string
arguments. As you saw in the previous example, passing a user-defined
logger as the first argument allows you to specify the parent logger for
tracing. You may also pass a variable number of method names as
arguments to ``traced``.
Autologging will then trace only the methods that are named (assuming
that they are defined in the class body). And as in the previous
example, you may still choose whether or not to pass in a named logger
as the *first* argument (not shown below).

::

   # my_module.py

   from autologging import traced


   @traced("my_method", "__eq__")
   class MyClass:

      def __init__(self):
         self._value = "ham"

      def my_method(self, arg, keyword=None):
         return "%s, %s, and %s" % (arg, self._value, keyword)

      def __eq__(self, other):
         return False

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import MyClass
   >>> my_obj = MyClass()  # __init__ is not in the list, so not traced
   >>> my_obj.my_method("spam", keyword="eggs")
   TRACE:my_module.MyClass:my_method:CALL *('spam',) **{'keyword': 'eggs'}
   TRACE:my_module.MyClass:my_method:RETURN 'spam, ham, and eggs'
   'spam, ham, and eggs'
   >>> my_obj == 79  # __eq__ is explicitly named in the list
   TRACE:my_module.MyClass:__eq__:CALL *(79,) **{}
   TRACE:my_module.MyClass:__eq__:RETURN False
   False

.. _traced-generators:

Trace a generator iterator
==========================

.. versionadded:: 1.2.0

`Generator <https://docs.python.org/3/glossary.html#term-generator>`_
functions employ the ``yield`` keyword in the function body, instructing
Python to create (and return) a `generator iterator
<https://docs.python.org/3/glossary.html#term-generator-iterator>`_ when
the function is invoked::

   # my_module.py

   from autologging import traced


   @traced
   class MyClass:

       def my_iter(self, word):
           for character in reversed(word):
               yield character.upper()

To observe how Autologging traces both the *generator* and its
returned *generator iterator*, assume we run the program like so::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import MyClass
   >>> my_obj = MyClass()
   >>> for c in my_obj.my_iter("spam"):
   ...     print(c)
   ... 
   (continued below)


Because the *generator* function ``my_iter`` is traced, Autologging will
dutifully emit the CALL/RETURN trace logging records::

   TRACE:my_module.MyClass:my_iter:CALL *('spam',) **{}
   TRACE:my_module.MyClass:my_iter:RETURN <generator object MyClass.my_iter at 0x7f54f4043840>
   (continued below)

In versions of Autologging **prior to 1.2.0**, this would be the only
tracing output. But as of version 1.2.0, the *generator iterator* is
now traced as well, and will emit additional YIELD/STOP trace logging
records::

   TRACE:my_module.MyClass:my_iter:YIELD 'M'
   M
   TRACE:my_module.MyClass:my_iter:YIELD 'A'
   A
   TRACE:my_module.MyClass:my_iter:YIELD 'P'
   P
   TRACE:my_module.MyClass:my_iter:YIELD 'S'
   S
   TRACE:my_module.MyClass:my_iter:STOP

.. _traced-nested-class:

Trace a nested class
====================

Tracing a nested class is no different than tracing a module-level
class::

   # my_module.py

   from autologging import traced


   class MyClass:

      @traced
      class Nested:

         def do_something(self):
            pass

.. note::
   Under Python 3.3+, Autologging will use a class's qualified name
   (:pep:`3155`) when creating loggers. In this example, the tracing
   log entries will be logged using the name "my_module.MyClass.Nested".
   (Under versions of Python <3.3, where "__qualname__" is not
   available, the logger name would be simply "my_module.Nested".)

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import MyClass
   >>> nested = MyClass.Nested()
   >>> nested.do_something()
   TRACE:my_module.MyClass.Nested:do_something:CALL *() **{}
   TRACE:my_module.MyClass.Nested:do_something:RETURN None

.. _module-traced-function:

Trace a function using a module-named logger
============================================

::

   # my_module.py

   from autologging import traced


   @traced
   def my_function(arg, keyword=None):
      return "%s and %s" % (arg, keyword)

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import my_function
   >>> my_function("spam", keyword="eggs")
   TRACE:my_module:my_function:CALL *('spam',) **{'keyword': 'eggs'}
   TRACE:my_module:my_function:RETURN 'spam and eggs'
   'spam and eggs'

.. _named-traced-function:

Trace a function using a user-named logger
==========================================

::

   # my_module.py

   import logging
   from autologging import traced


   @traced(logging.getLogger("my.app"))
   def my_function(arg, keyword=None):
      return "%s and %s" % (arg, keyword)

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import my_function
   >>> my_function("spam", keyword="eggs")
   TRACE:my.app:my_function:CALL *('spam',) **{'keyword': 'eggs'}
   TRACE:my.app:my_function:RETURN 'spam and eggs'
   'spam and eggs'

.. _traced-nested-function:

Trace a nested function
=======================

::

   # my_module.py

   from autologging import traced


   def my_function(arg, keyword=None):
      @traced
      def nested_function(word1, word2):
         return "%s and %s" % (word1, word2)
      return nested_function(arg, keyword if (keyword is not None) else "eggs")

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import my_function
   >>> my_function("spam")
   TRACE:my_module:nested_function:CALL *('spam', 'eggs') **{}
   TRACE:my_module:nested_function:RETURN 'spam and eggs'
   'spam and eggs'

