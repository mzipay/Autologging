========================================================================
Autologging --- easier logging and tracing for classes
========================================================================

http://www.ninthtest.net/python-autologging/
Matthew Zipay <mattz@ninthtest.net>
MIT License (see the LICENSE.txt file)

Python 2.7, 3.2, 3.3

------------------------------------------------------------------------
INTRODUCTION
------------------------------------------------------------------------

Autologging provides two decorators and a metaclass factory:

@logged
- creates a class-level '__logger' member
- the logger is automatically named to match the dotted-name of the
  class; or provider a specific logger

@traced
- decorates a module-level function to provide call/return tracing
- log record attributes (pathname, filename, lineno, module, funcName)
  are correctly preserved (i.e. they refer to the original function, NOT
  the proxy function returned by the decorator)

TracedMethods
- creates a metaclass that adds automatic tracing to specified class
  methods (just like @traced does for module-level functions)
- log record attributes (pathname, filename, lineno, module, funcName)
  are correctly preserved (i.e. they refer to the original class method,
  NOT the proxy method installed by the metaclass)

Additionally, the autologging module defines and registers a custom
log level named "TRACE" (level 1) so that tracing messages can be
toggled on/off independently of DEBUG-level logging.

------------------------------------------------------------------------
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
