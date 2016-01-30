================================
Disabling ``@traced`` at runtime
================================

:Release: |release|

.. versionadded:: 1.1.0

* :ref:`automatic-noop`
* :ref:`explicit-noop`

When a class or a function is decorated with :func:`autologging.traced`,
Autologging *replaces* a method (or function) with a tracing "proxy"
function that intercepts any invocation to perform the CALL/RETURN
tracing. (See :doc:`internals` for a more in-depth explanation.)

Autologging is careful to minimize the overhead imposed by these tracing
proxy functions, but there will always be *some* overhead - even when
the :attr:`autologging.TRACE` log level is disabled, the tracing proxy
function must still (a) check the log level and then (b) delegate to
the original method/function.

In some cases, it may be desirable to completely eliminate *any* tracing
overhead. Running the application in a production environment, or
executing a performance test, are the two most obvious examples. For
these cases, Autologging now provides a "killswitch" for the ``@traced``
decorator that effectively turns it into a no-op.

When the :func:`autologging.install_traced_noop` function is called
**before** the traced decorator is imported and any classes or functions
have been decorated, then the ``@traced`` decorator will function as an
"identity" decorator, simply returning the decorated class or function
**unmodified**. In this way, tracing can be completely "removed" from an
application *without* having to comment-out the ``@traced`` decorator
(or conditionally apply it).

.. warning::
   Calling ``autologging.install_traced_noop()`` *after* any class or
   function has been decorated **will not uninstall the tracing proxy
   function.** It is imperative that
   ``autologging.install_traced_noop()`` be called *before*
   :func:`autologging.traced` is imported and before any class or
   function is decorated.

   The process is irreversible in the running Python interpreter. Once
   ``autologging.install_traced_noop()`` has been called, the only way
   to reinstate tracing functionality is to restart the interpreter (and
   *not* install the no-op).

Consider a simple application consisting of two modules - a bootstrap
module that is responsible for launching the application, and the
application module itself:

::

   # bootstrap.py

   import app

   if __name__ == "__main__":
       app.launch()

::

   # app.py

   from autologging import traced


   @traced
   class Application:

      def __init__(self):
         self._prepare_connections()
         # other initialization

      def _prepare_connections(self):
         # prepare the connections

      def run(self):
         while True:
            # listen for events, then handle them

      def handle(self, event):
         # handle the event


   @traced
   def launch():
      Application().run()

As written, the "__init__", "_prepare_connections", "run", and "handle"
methods of the application object, and the "launch" function in the
``app`` module,  will be replaced by tracing proxies.

.. note::
   Whether or not any tracing info is *emitted* to logs can be
   controlled simply by configuring the logging system appropriately.

Let's suppose that for this particular application we wish to completely
*remove* tracing capability when running in a production or performance
testing environment. To accomplish this, we need to call the
:func:`autologging.install_traced_noop` function **before** any class or
function is decorated with ``@traced``.

.. _automatic-noop:

Recommended approach: Let Autologging install the ``@traced`` no-op automatically
=================================================================================

The recommended approach is to instruct Autologging to install the no-op
automatically. This can be accomplished by setting the
``AUTOLOGGING_INSTALL_TRACED_NOOP`` environment variable to a value such
that ``bool(os.getenv("AUTOLOGGING_INSTALL_TRACED_NOOP"))`` evaluates to
``True``.

For example, we would run the application in a production or performance
testing environment like so::

   $ export AUTOLOGGING_INSTALL_TRACED_NOOP=True
   $ python bootstrap.py

.. note::
   This is the recommended approach because it requires no change to the
   application or bootstrap source code.

   If the conditions under which tracing should be deactivated are more
   complex, then direct installation of the ``@traced`` no-op may be
   necessary.

.. _explicit-noop:

Install the ``@traced`` no-op directly
======================================

If automatic installation of the ``@traced`` no-op is not possible (or
not preferred), then the application bootstrap code can be modified to
install the no-op directly.

The following modification to *bootstrap.py* accomplishes the goal::

   # bootstrap.py

   import os
   import autologging

   # MUST happen before importing app!
   if os.getenv("APP_ENV") in ("PRODUCTION", "PERFORMACE_TEST"):
      autologging.install_traced_noop()

   import app

   if __name__ == "__main__":
       app.launch()

