# -*- coding: utf-8 -*-

from setuptools import setup

setup(name="Autologging",
      version="0.1",
      description="Autologging is a module containing decorators and a "
                  "metaclass used to make logging classes easier.",
      long_description="""\
Autologging provides two decorators and a metaclass factory:

@logged
- creates a class-level '__logger' member
- the logger is automatically named to match the dotted-name of the class

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

Autologging runs on Python 2.7 and 3.2+.
""",
    author="Matthew Zipay",
    author_email="mattz@ninthtest.net",
    url="http://www.ninthtest.net/python-autologging/",
    download_url = "https://sourceforge.net/projects/autologging/files/",
    py_modules=["autologging"],
    test_suite="test.suite",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    license="MIT License",
    keywords=["logging", "tracing"]
)
