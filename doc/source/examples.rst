=================================
Examples of using ``autologging``
=================================

Following are two examples of using :mod:`autologging`. The first example uses
"default" (named for the containing module) loggers, while the second example
shows how to exercise more control in order to separate logging from tracing.

The examples are given in Python 3 syntax (the only change that needs to be
made for these examples to under on Python 2.7 is to modify the metaclass
syntax).

Using the default (module-named) logger for both logging and tracing
====================================================================

In a module *my_module.py*::

   import logging

   from autologging import logged, traced, TracedMethods

   _logger = logging.getLogger(__name__)


   @traced
   def my_function():
      _logger.debug("debug message from a traced function")


   @logged
   def my_other_function():
      my_other_function.__logger.info("info message from a logged function")


   @logged
   class MyClass(metaclass=TracedMethods("my_classmethod", "my_method")):

      @logged
      class Inner:

         def my_inner_method(self):
            self.__logger.info("info message from a NON-traced inner class method")

      @staticmethod
      def my_staticmethod():
         MyClass.__logger.info("info message from a NON-traced static method")

      @classmethod
      def my_classmethod(cls):
         cls.__logger.warning("warning message from a traced class method")

      def my_method(self):
         self.__logger.debug("debug message from a traced instance method")

      def another_method(self):
         self.__logger.info("info message from a NON-traced instance method")

Log output
----------

Assuming the default log format (*"%(levelname)s:%(name)s:%(message)s"*) and a
log level set to :data:`autologging.TRACE`, calling each of the functions and
methods above (in their defined order) would produce the following log output::

   TRACE:my_module:CALL my_function *() **{}
   DEBUG:my_module:debug message from a traced function
   TRACE:my_module:RETURN my_function None
   INFO:my_module:info message from a logged function
   INFO:my_module.MyClass.Inner:info message from a NON-traced inner class method")
   INFO:my_module.MyClass:info message from a NON-traced static method
   TRACE:my_module.MyClass:CALL MyClass.my_classmethod *() **{}
   WARNING:my_module.MyClass:warning message from a traced class method
   TRACE:my_module.MyClass:RETURN MyClass.my_classmethod None
   TRACE:my_module.MyClass:CALL MyClass.my_method *() **{}
   DEBUG:my_module.MyClass:debug message from a traced instance method
   TRACE:my_module.MyClass:RETURN MyClass.my_method *() **{}
   INFO:my_module.MyClass:info message from a NON-traced instance method

Using different named loggers for logging and tracing
=====================================================

In a module *my_module.py*::

   import logging

   from autologging import logged, traced, TracedMethods

   _logger = logging.getLogger("myapp")
   _tracer = logging.getLogger("myapp.tracing")


   @traced(_tracer)
   def my_function():
      _logger.debug("debug message from a traced function")


   @logged(_logger)
   def my_other_function():
      my_other_function.__logger.info("info message from a logged function")


   @logged(_logger)
   class MyClass(
         metaclass=TracedMethods(_tracer, "my_classmethod", "my_method")):

      @logged(_logger)
      class Inner:

         def my_inner_method(self):
            self.__logger.info("info message from a NON-traced inner class method")

      @staticmethod
      def my_staticmethod():
         MyClass.__logger.info("info message from a NON-traced static method")

      @classmethod
      def my_classmethod(cls):
         cls.__logger.warning("warning message from a traced class method")

      def my_method(self):
         self.__logger.debug("debug message from a traced instance method")

      def another_method(self):
         self.__logger.info("info message from a NON-traced instance method")

Log output
----------

Assuming the default log format (*"%(levelname)s:%(name)s:%(message)s"*) and a
log level set to :data:`autologging.TRACE`, calling each of the functions and
methods above (in their defined order) would produce the following log output::

   TRACE:myapp.tracing:CALL my_function *() **{}
   DEBUG:myapp:debug message from a traced function
   TRACE:myapp.tracing:RETURN my_function None
   INFO:myapp:info message from a logged function
   INFO:myapp.MyClass.Inner:info message from a NON-traced inner class method
   INFO:myapp.MyClass:info message from a NON-traced static method
   TRACE:myapp.tracing.MyClass:CALL MyClass.my_classmethod *() **{}
   WARNING:myapp.MyClass:warning message from a traced class method
   TRACE:myapp.tracing.MyClass:RETURN MyClass.my_classmethod None
   TRACE:myapp.tracing.MyClass:CALL MyClass.my_method *() **{}
   DEBUG:myapp.MyClass:debug message from a traced instance method
   TRACE:myapp.tracing.MyClass:RETURN MyClass.my_method *() **{}
   INFO:myapp.MyClass:info message from a NON-traced instance method

