===============================
Using the ``@logged`` decorator
===============================

:Release: |release|

* :ref:`module-logged-class`
* :ref:`named-logged-class`
* :ref:`logged-nested-class`
* :ref:`module-logged-function`
* :ref:`named-logged-function`
* :ref:`logged-nested-function`

.. _module-logged-class:

Add a module-named logger to a class
====================================

::

   # my_module.py
    
   from autologging import logged
    
    
   @logged
   class MyClass:

       @staticmethod
       def my_staticmethod():
           MyClass.__log.info("my message")

       @classmethod
       def my_classmethod(cls):
           cls.__log.info("my message")
    
       def my_method(self):
           self.__log.info("my message")

>>> import logging, sys
>>> logging.basicConfig(
...     level=logging.INFO, stream=sys.stdout,
...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
>>> from my_module import MyClass
>>> MyClass.my_staticmethod()
INFO:my_module.MyClass:my_staticmethod:my message
>>> MyClass.my_classmethod()
INFO:my_module.MyClass:my_classmethod:my message
>>> my_obj = MyClass()
>>> my_obj.my_method()
INFO:my_module.MyClass:my_method:my message

.. _named-logged-class:

Add a user-named logger to a class
===================================

::

   # my_module.py
    
   import logging
   from autologging import logged
    
    
   @logged(logging.getLogger("my.app"))
   class MyClass:

       @staticmethod
       def my_staticmethod():
           MyClass.__log.info("my message")

       @classmethod
       def my_classmethod(cls):
           cls.__log.info("my message")
    
       def my_method(self):
           self.__log.info("my message")

>>> import logging, sys
>>> logging.basicConfig(
...     level=logging.INFO, stream=sys.stdout,
...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
>>> from my_module import MyClass
>>> MyClass.my_staticmethod()
INFO:my.app.MyClass:my_staticmethod:my message
>>> MyClass.my_classmethod()
INFO:my.app.MyClass:my_classmethod:my message
>>> my_obj = MyClass()
>>> my_obj.my_method()
INFO:my.app.MyClass:my_method:my message

.. _logged-nested-class:

Add a logger to a nested class
==============================

::

   # my_module.py
    
   from autologging import logged
    
    
   @logged
   class MyClass:
    
      @logged
      class _Nested:
       
         def __init__(self):
            self.__log.info("my message")
    
      def my_method(self):
         self.__log.info("my message")
         nested = self._Nested()

>>> import logging, sys
>>> logging.basicConfig(
...     level=logging.INFO, stream=sys.stdout,
...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
>>> from my_module import MyClass
>>> my_obj = MyClass()
>>> my_obj.my_method()
INFO:my_module.MyClass:my_method:my message
INFO:my_module.MyClass._Nested:__init__:my message

.. _module-logged-function:

Add a module-named logger to a function
=======================================

::

   # my_module.py
    
   from autologging import logged
    
    
   @logged
   def my_function():
       my_function._log.info("my message")

>>> import logging, sys
>>> logging.basicConfig(
...     level=logging.INFO, stream=sys.stdout,
...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
>>> from my_module import my_function
>>> my_function()
INFO:my_module:my_function:my message

.. _named-logged-function:

Add a user-named logger to a function
=====================================

::

   # my_module.py
    
   import logging
   from autologging import logged
    
    
   @logged(logging.getLogger("my.app"))
   def my_function():
       my_function._log.info("my message")

>>> import logging, sys
>>> logging.basicConfig(
...     level=logging.INFO, stream=sys.stdout,
...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
>>> from my_module import my_function
>>> my_function()
INFO:my.app:my_function:my message

.. _logged-nested-function:

Add a logger to a nested function
=================================

::

   # my_module.py
    
   from autologging import logged
    
   @logged
   def my_function():
      @logged
      def nested_function():
         nested_function._log.info("my message")
      my_function._log.info("my message")
      nested_function()

>>> import logging, sys
>>> logging.basicConfig(
...     level=logging.INFO, stream=sys.stdout,
...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
>>> from my_module import my_function
>>> my_function()
INFO:my_module:my_function:my message
INFO:my_module:nested_function:my message

