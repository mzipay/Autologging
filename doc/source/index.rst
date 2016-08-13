=============================================================
Autologging --- easier logging and tracing for Python classes
=============================================================

:Release: |release|

.. image:: https://img.shields.io/pypi/v/Autologging.svg
   :alt: PyPI version
   :target: https://pypi.python.org/pypi/Autologging

.. image:: https://img.shields.io/pypi/pyversions/Autologging.svg
   :alt: Python version
   :target: https://www.python.org/

.. image:: https://img.shields.io/pypi/implementation/Autologging.svg
   :alt: Python implementation
   :target: https://pypi.python.org/pypi/Autologging

.. image:: https://img.shields.io/pypi/l/Autologging.svg
   :alt: License
   :target: https://github.com/mzipay/Autologging/blob/master/LICENSE.txt

.. image:: https://img.shields.io/pypi/wheel/Autologging.svg
   :alt: Wheel availability
   :target: https://pypi.python.org/pypi/Autologging

Autologging eliminates boilerplate logging setup code and tracing code,
and provides a means to separate application logging from program flow
and data tracing.

Python modules that make use of Autologging are cleaner, leaner, and
more resilient to changes that would otherwise require updating tracing
statements.

Autologging allows for tracing to be configured (and controlled)
independently from application logging. Toggle tracing on/off, write
trace log records to a separate log, and use different formatting for
trace log entries - all via standard Python logging facilities, and
without affecting your application logging.

**Python 2.7 and Python 3.3+ are supported using the same codebase.**
All examples given on this site use Python 3 syntax.

.. versionadded:: 1.0.1
   Autologging is now officially tested and working under `Jython
   <http://www.jython.org/>`_, `IronPython <http://ironpython.net/>`_,
   `PyPy <http://pypy.org/>`_, and `Stackless Python
   <https://bitbucket.org/stackless-dev/stackless/wiki/Home>`_.

Autologging exposes two decorators (:func:`autologging.logged`,
:func:`autologging.traced`) and a custom log level
(:attr:`autologging.TRACE`).

.. versionadded:: 1.1.0
   Autologging now exposes the :func:`autologging.install_traced_noop`
   function. This function **replaces** the ``traced`` decorator with a
   no-op that returns traced classes and functions unmodified
   (effectively disabling all tracing capabilities). This is useful for
   cases where *any* overhead from tracing is not desired (for example,
   when running in production environments, or when running performance
   tests).

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   intro
   autologging
   examples
   internals

Download and Install
--------------------

The easiest way to install Autologging is to use `pip
<https://pip.pypa.io/>`_::

   $ pip install Autologging

To install from source, clone or fork the repository::

   $ git clone https://github.com/mzipay/Autologging.git

Alternatively, download and extract a source .zip or .tar.gz archive
from https://github.com/mzipay/Autologging/releases or
https://pypi.python.org/pypi/Autologging.

Run the test suite and install the ``autologging`` module (make sure you
have `setuptools <https://pypi.python.org/pypi/setuptools>`_
installed!)::

   $ cd Autologging
   $ python setup.py test
   $ python setup.py install

You can also install from one of the available binary packages
available at https://pypi.python.org/pypi/Autologging or
https://sourceforge.net/projects/autologging/files/.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

