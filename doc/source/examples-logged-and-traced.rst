==========================================
Using ``@logged`` and ``@traced`` together
==========================================

:Release: |release|

* :ref:`logged-traced-class`
* :ref:`logged-traced-function`

.. _logged-traced-class:

Add logging and tracing to a class
==================================

::

   # my_module.py

   from autologging import logged, traced


   @traced
   @logged
   class MyClass:

      def __init__(self, value):
         self.__log.info("I like %s.", value)
         self._value = value

      def my_method(self, arg, keyword=None):
         return "%s, %s, and %s" % (arg, self._value, keyword)

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import MyClass
   >>> my_obj = MyClass("ham")
   TRACE:my_module.MyClass:__init__:CALL *('ham',) **{}
   INFO:my_module.MyClass:__init__:I like ham.
   TRACE:my_module.MyClass:__init__:RETURN None
   >>> my_obj.my_method("spam", keyword="eggs")
   TRACE:my_module.MyClass:my_method:CALL *('spam',) **{'keyword': 'eggs'}
   TRACE:my_module.MyClass:my_method:RETURN 'spam, ham, and eggs'
   'spam, ham, and eggs'

.. _logged-traced-function:

Add logging and tracing to a function
=====================================

.. warning::
   Although the ``@logged`` and ``@traced`` decorators will "do the
   right thing" regardless of the order in which they are applied to the
   same function, it is recommended that ``@logged`` always be used as
   the innermost decorator.

   This is because ``@logged`` simply sets the logger member and then
   returns the original function, making it safe to use in combination
   with any other decorator.

::

   # my_module.py

   from autologging import logged, traced


   @traced
   @logged
   def my_function(arg, keyword=None):
      my_function._log.info("my message")
      return "%s and %s" % (arg, keyword)

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import my_function
   >>> my_function("spam", keyword="eggs")
   TRACE:my_module:my_function:CALL *('spam',) **{'keyword': 'eggs'}
   INFO:my_module:my_function:my message
   TRACE:my_module:my_function:RETURN 'spam and eggs'
   'spam and eggs'

