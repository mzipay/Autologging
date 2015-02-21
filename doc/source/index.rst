=============================================================
Autologging --- easier logging and tracing for Python classes
=============================================================

:Release: |release|

The :mod:`autologging` module defines two decorators and a metaclass factory
that make :py:mod:`logging` easier to use with classes.

Python 2.7 and Python 3.2+ are supported using the same codebase. All examples
given on this site use Python 3 syntax.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   intro
   autologging
   examples

Download and Install
--------------------

* Use "`pip <https://pypi.python.org/pypi/pip>`_ install Autologging".
* Download a source or built distribution from `Autologging on SourceForge
  <http://sourceforge.net/projects/autologging/files/autologging/>`_ and run
  either *setup.py* or the binary installer.
* Clone the `Autologging Mercurial repository from BitBucket
  <https://bitbucket.org/mzipay/autologging>`_ and run *setup.py*.

If you download or clone the source, the test suite can be run from the
project root directory in either of the following ways::

   python -m unittest test.suite

or::

   python setup.py test

There are also a number of :mod:`doctest` tests embedded within Autologging's
docstrings (written using Python 3 syntax). If you are running Python 3.2+, you
can run the doctests like so::

   python -m doctest autologging.py

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

