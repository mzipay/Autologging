Autologging - easier logging and tracing for classes
========================================================================

HOMEPAGE:
   http://www.ninthtest.net/python-autologging/

AUTHOR:
   Matthew Zipay <mattz@ninthtest.net>

LICENSE:
   MIT License (see the LICENSE.txt file)

PYTHON COMPATIBILITY:
   Python 2.7, 3.2+


INTRODUCTION
------------------------------------------------------------------------

Autologging provides two decorators and a metaclass factory:

**logged**
   Decorate a class (or function) to create a ``__logger`` member.
   The logger is automatically named to match the dotted-name of the
   class or module.
   Alternatively, provide a specific logger by passing it to the
   decorator (i.e. ``logged(my_logger)``).

**traced**
   Decorate a module-level function to provide call/return tracing.
   The log record attributes *pathname*, *filename*, *lineno*, *module*,
   and *funcName* work as expected (i.e. they refer to the original
   function, NOT the proxy function returned by the decorator).

**TracedMethods**
   Create a metaclass that adds automatic tracing to specified class
   methods (just like ``traced`` does for module-level functions).
   The log record attributes *pathname*, *filename*, *lineno*, *module*,
   and *funcName* work as expected (i.e. they refer to the original
   class method, NOT the proxy method installed by the metaclass).

Additionally, an ``autologging.TRACE`` (level 1) custom log level is
registered with the Python ``logging`` module so that tracing messages
can be toggled on/off independently of DEBUG-level logging.


DOWNLOAD / INSTALL
------------------------------------------------------------------------

There are three options to download/install Autologging:

* Use "pip install Autologging"
* Download a source or built distribution from
  http://sourceforge.net/projects/autologging/files/autologging/
  and run either "python setup.py" or the binary installer
* Clone the Mercurial repository from
  https://bitbucket.org/mzipay/autologging and run "python setup.py"

If you download or clone the source, the test suite can be run from the
project root directory in either of the following ways:

   python -m unittest test.suite

   python setup.py test

There are also a number of :mod:`doctest` tests embedded within Autologging's
docstrings (written using Python 3 syntax). If you are running Python 3.2+, you
can run the doctests like so:

   python -m doctest autologging.py

