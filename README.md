# Autologging - easier logging and tracing for Python classes

http://ninthtest.info/python-autologging/

[![PyPI version](https://img.shields.io/pypi/v/Autologging.svg)](https://pypi.python.org/pypi/Autologging)
[![Python version](https://img.shields.io/pypi/pyversions/Autologging.svg)](https://pypi.python.org/pypi/Autologging)
[![Python implementation](https://img.shields.io/pypi/implementation/Autologging.svg)](https://pypi.python.org/pypi/Autologging)
[![License](https://img.shields.io/pypi/l/Autologging.svg)](https://github.com/mzipay/Autologging/blob/master/LICENSE.txt)
[![Wheel availability](https://img.shields.io/pypi/wheel/Autologging.svg)](https://pypi.python.org/pypi/Autologging)

## Introduction

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

### What's in the `autologging` namespace?

Autologging exposes two decorators and a custom log level:

**`logged`**
Decorate a class to create a `__log` member. The logger is named by
default to match the dotted-name of the containing class. A function
may also be decorated, creating a `_log` attribute on the function
object whose default name matches the containing module.
A specifically-named logger may also be passed to the decorator (i.e.
`logged(my_logger)`).

**`traced`**
Decorate a class to provide **automatic** method call/return tracing. By
default, all class, static, and instance methods are traced (excluding
"__special__" methods, with the exception of `__init__` and `__call__`).
As with the `logged` decorator, the default name of the tracing logger
matches the dotted-name of the containing class and may be overridden by
passing a specifically-named logger to the decorator.
Additionally, this decorator accepts multiple string arguments that
explicitly name the methods to be traced (and may even name
"__special__" methods).

Module-level functions may also be traced using this decorator.

*New in version 1.2.0:* automatic yield/stop tracing of Python
[generator iterators](https://docs.python.org/3/glossary.html#term-generator-iterator)
(if the [generator](https://docs.python.org/3/glossary.html#term-generator)
function is traced).

**`TRACE`**
The `autologging.TRACE` (level 1) log level is registered with the
Python `logging` module when Autologging is imported so that tracing
can be configured and controlled independently of application logging.

Tracing may be disabled entirely by setting the
`AUTOLOGGING_TRACED_NOOP` environment variable or by calling the
`autologging.install_traced_noop()` function.

## A brief example

A simple logged and traced class:

```python
 1 import logging
 2 import sys
 3
 4 from autologging import logged, TRACE, traced
 5
 6 @traced
 7 @logged
 8 class Example:
 9
10     def __init__(self):
11         self.__log.info("initialized")
12
13     def backwards(self, *words):
14         for word in words:
15             yield "".join(reversed(word))
16
17
18 if __name__ == "__main__":
19     logging.basicConfig(
20             level=TRACE, stream=sys.stderr,
21             format="%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s")
22     example = Example()
23     for result in example.backwards("spam", "eggs"):
24         print(result)
```

Logging and tracing output:

```bash
$ python example.py
TRACE:example.py,10:__main__.Example.__init__:CALL *() **{}
INFO:example.py,11:__main__.Example.__init__:initialized
TRACE:example.py,13:__main__.Example.backwards:CALL *('spam', 'eggs') **{}
TRACE:example.py,15:__main__.Example.backwards:RETURN <generator object backwards at 0x7fa534d61eb0>
TRACE:example.py,15:__main__.Example.backwards:YIELD 'maps'
maps
TRACE:example.py,15:__main__.Example.backwards:YIELD 'sgge'
sgge
TRACE:example.py,15:__main__.Example.backwards:STOP
```

## Installation

The easiest way to install Autologging is to use
[pip](https://pip.pypa.io/):

```bash
$ pip install Autologging
```

### Source installation

Clone or fork the repository:

```bash
$ git clone https://github.com/mzipay/Autologging.git
```

Alternatively, download and extract a source .zip or .tar.gz archive
from https://github.com/mzipay/Autologging/releases,
https://pypi.python.org/pypi/Autologging or
https://sourceforge.net/projects/autologging/files/.

Run the test suite and install the `autologging` module: (make sure you
have [setuptools](https://pypi.python.org/pypi/setuptools) installed!)

```bash
$ cd Autologging
$ python setup.py test
$ python setup.py install
```

### Binary installation

Download the Python wheel (.whl) or a Windows installer from
https://pypi.python.org/pypi/Autologging or
https://sourceforge.net/projects/autologging/files/.

(Use [pip](https://pip.pypa.io/) or
[wheel](https://pypi.python.org/pypi/wheel) to install the .whl.)

