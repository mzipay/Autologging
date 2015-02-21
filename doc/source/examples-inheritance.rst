=================================
Logging, tracing, and inheritance
=================================

Autologging's policy on inheritance is simple:

**Loggers are never inherited, and inherited methods are never traced.**

Practically speaking, this means that you must be explicit when using
:func:`autologging.logged` and :func:`autologging.TracedMethods` throughout a
class's bases.

If a class in the hierarchy will use a logger, then *that* class definition
must be ``@logged``. Likewise, if a method inherited from a super class in the
hierarchy will be traced, then either *that* super class must use the
``TracedMethods`` metaclass factory, or the method must be overridden (and then
traced) in a subclass.

The following example illustrates these concepts::

   # my_module.py

   from autologging import logged, TracedMethods


   @logged
   class Base(metaclass=TracedMethods()):

      # this method will be traced
      def method(self):
         # log channel will be "my_module.Base"
         self.__logger.info("base message")
         return "base"


   @logged
   class Parent(Base):

      # this method will NOT be traced
      def method(self):
         # log channel will be "my_module.Parent"
         self.__logger.info("parent message")
         return super().method() + ",parent"


   class Child(Parent, metaclass=TracedMethods()):

      # this method will be traced
      def method(self):
         return super().method() + ",child"

::

   >>> import logging, sys
   >>> from autologging import TRACE
   >>> logging.basicConfig(level=TRACE, stream=sys.stdout,
   ...     format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")
   >>> from my_module import Child
   >>> child = Child()
   >>> child.method()
   TRACE:my_module.Child:method:CALL *() **{}
   INFO:my_module.Parent:method:parent message
   TRACE:my_module.Base:method:CALL *() **{}
   INFO:my_module.Base:method:base message
   TRACE:my_module.Base:method:RETURN 'base'
   TRACE:my_module.Child:method:RETURN 'base,parent,child'
   'base,parent,child'

