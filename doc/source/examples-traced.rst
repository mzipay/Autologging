===========================================================================
Using the ``TracedMethods`` metaclass factory and the ``@traced`` decorator
===========================================================================

:Release: |release|

* :ref:`module-traced-class`
* :ref:`named-traced-class`
* :ref:`specific-traced-methods`
* :ref:`traced-nested-class`
* :ref:`module-traced-function`
* :ref:`named-traced-function`
* :ref:`traced-nested-function`

.. warning::
   The ``@traced`` decorator will not work as you might expect for methods of
   a class. In general, prefer to use the ``TracedMethods`` metaclass factory
   for tracing methods of a class, and the ``@traced`` decorator for tracing
   functions defined outside of classes.

.. _module-traced-class:

Trace all methods of a class using a module-named logger
========================================================

This is the simplest way to use :func:`autologging.TracedMethods`. All
*non-special* methods of the class are traced to a logger that is named after
the containing module and class. (Note: the special ``__init__`` method is an
exception to the rule - it is traced by default if it is defined.)

.. note::
   Inherited methods are **never** traced. If you want tracing for inherited
   methods, either trace them in the super class, or override them in the
   subclass.

::

   # my_module.py

   from autologging import TracedMethods


   class MyClass(metaclass=TracedMethods()):

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

This example is identical to the above example, except that the tracing logger
has a user-defined name ("tracing.example" in this case). Simply pass the
user-defined logger as the first positional argument to ``TracedMethods``::

   # my_module.py

   import logging
   from autologging import TracedMethods

   _logger = logging.getLogger("tracing.example")


   class MyClass(metaclass=TracedMethods(_logger)):

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

The ``TracedMethods`` metaclass factory accepts a variable number of positional
arguments. As you saw in the previous example, passing a user-defined logger as
the first argument allows you to specify the parent logger for tracing. You may
also pass a variable number of method names as arguments to ``TracedMethods``.
Autologging will then trace only the methods that are named (assuming that they
are defined in the class body). And as in the previous example, you may still
choose whether or not to pass in a parent logger.

::

   # my_module.py

   from autologging import TracedMethods


   class MyClass(metaclass=TracedMethods("my_method", "__eq__")):

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

.. _traced-nested-class:

Trace a nested class
====================

Tracing a nested class is no different than tracing a top-level class::

   # my_module.py

   from autologging import TracedMethods


   class MyClass:

      class Nested(metaclass=TracedMethods()):

         def do_something(self):
            pass

.. note::
   Under Python 3.3+, Autologging will use a class's qualified name
   (:pep:`3155`) when creating loggers. In this example, the tracing
   log entries will be logged using the name "my_module.MyClass.Nested".

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

