==============================
How does ``autologging`` work?
==============================

:Release: |release|

The :func:`autologging.logged` decorator is rather boring - it simply
creates a :class:`logging.Logger` object and sets it as an attribute
of the decorated class (or function).

However, in order to automate tracing while **preserving** introspection
and subclassing capabilities, the :func:`autologging.traced` decorator
has a tougher job.

To trace the call and return of a particular function, Autologging
performs the following steps:

1. Intercept the function call, capturing all positional and keyword
   arguments that were passed.
2. Log the call at the :attr:`autologging.TRACE` log level.
3. Call the *original* function, passing the positional and keyword
   arguments, and capturing the return value.
4. Log the return at the :attr:`autologging.TRACE` log level.
5. Return the value.

Autologging installs a **replacement** function for any traced class
method or function. That replacement function is responsible for the
steps described above.

.. note::
   If the ``TRACE`` level is disabled for the tracing logger when a
   traced function is called, the replacement function delegates
   directly to the original function.

.. rubric:: Which functions are traced?

A quick way to determine which functions have been traced is to look for
the ``__autologging_traced__`` attribute. Autologging sets this
attribute to the value ``True`` on every replacement function. For
example:

>>> from autologging import traced
>>> @traced
... def example():
...     return "OK"
... 
>>> hasattr(example, "__autologging_traced__")
True
>>> @traced
... class Example:
...     @classmethod
...     def class_method(cls):
...         return "OK"
...     @staticmethod
...     def static_method():
...         return "OK"
...     def method(self):
...         return "OK"
... 
>>> hasattr(Example.class_method, "__autologging_traced__")
True
>>> hasattr(Example.static_method, "__autologging_traced__")
True
>>> hasattr(Example.method, "__autologging_traced__")
True

.. rubric:: Introspecting traced functions

When Autologging installs a replacement function for tracing, a
reference to the original function is stored as the ``__wrapped__``
attribute of the replacement function.

>>> from autologging import traced
>>> @traced
... def example():
        return "OK"
... 
>>> traced(example).__wrapped__ is example
True

>>> from autologging import traced
>>> @traced
... class Example:
...     def method(self):
...         return "OK"
... 
>>> original_method = Example.__dict__["method"]
>>> traced(Example).__dict__["method"].__wrapped__ is original_method
True

Traced :obj:`classmethod` and :obj:`staticmethod` functions are also
replaced by Autologging, but in addition to creating a replacement
function, Autologging also creates a replacement method descriptor. To
access the original function of a classmethod or staticmethod, you must
use the ``__wrapped__`` attribute *of the __func__ attribute* of the
replacement classmethod or staticmethod. An example makes this clear:

>>> from autologging import traced
>>> @traced
... class Example:
...     @classmethod
...     def class_method(cls):
...         return "OK"
...     @staticmethod
...     def static_method():
...         return "OK"
... 
>>> original_classmethod = Example.__dict__["class_method"]
>>> original_staticmethod = Example.__dict__["static_method"]
>>> Example = traced(Example)
>>> Example.__dict__["class_method"].__func__.__wrapped__ is original_classmethod.__func__
True
>>> Example.__dict__["static_method"].__func__.__wrapped__ is original_staticmethod.__func__
True

.. rubric:: Inheritance and subclassing with traced methods

Autologging is careful to not "break" assumptions about the types of
methods, or how those methods are inherited or overridden.

A replacement tracing method (or method descriptor, in the case of
classmethods and staticmethods) has the same type, name and signature as
the original method:

>>> import inspect
>>> from types import FunctionType, MethodType
>>> from autologging import traced
>>> @traced
... class Example:
...     @classmethod
...     def class_method(cls, arg, keyword=None):
...         return "OK"
...     @staticmethod
...     def static_method(arg, keyword=None):
...         return "OK"
...     def method(self, arg, keyword=None):
...         return "OK"
... 
>>> type(Example.__dict__["class_method"]) is classmethod
True
>>> Example.class_method.__name__
'class_method'
>>> inspect.signature(Example.class_method)
<Signature (arg, keyword=None)>
>>> type(Example.__dict__["static_method"]) is staticmethod
True
>>> Example.static_method.__name__
'static_method'
>>> inspect.signature(Example.static_method)
<Signature (arg, keyword=None)>
>>> type(Example.__dict__["method"]) is FunctionType
True
>>> type(Example().method) is MethodType
True
>>> Example.method.__name__
'method'
>>> inspect.signature(Example().method)
<Signature (arg, keyword=None)>

