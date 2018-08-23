=================================
Logging, tracing, and inheritance
=================================

:Release: |release|

Autologging's policy on inheritance is simple:

**Loggers are never inherited, and inherited methods are never traced.**

Practically speaking, this means that you must be explicit when using
:func:`autologging.logged` and :func:`autologging.traced` throughout a
class's bases.

If a class in the hierarchy will use a logger, then *that* class
definition must be ``@logged``. Likewise, if a method inherited from a
super class in the hierarchy will be traced, then either the method must
be traced in the *super* class or the method must be overridden (and
traced) in a subclass.

The following example illustrates these concepts::

   # my_module.py

   from autologging import logged, traced


   @traced
   @logged
   class Base:

      # this method will be traced
      def method(self):
         # log channel will be "my_module.Base"
         self.__log.info("base message")
         return "base"


   @logged
   class Parent(Base):

      # this method will NOT be traced
      def method(self):
         # log channel will be "my_module.Parent"
         self.__log.info("parent message")
         return super().method() + ",parent"


   @traced
   class Child(Parent):

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

