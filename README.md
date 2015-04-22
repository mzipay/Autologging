# Autologging - easier logging and tracing for Python classes

http://ninthtest.net/python-autologging/

[![Latest Version](https://pypip.in/version/Autologging/badge.svg?text=version)](https://pypi.python.org/pypi/Autologging/)
[![Supported Python versions](https://pypip.in/py_versions/Autologging/badge.svg)](https://pypi.python.org/pypi/Autologging/)
[![License](https://pypip.in/license/Autologging/badge.svg)](https://pypi.python.org/pypi/Autologging/)

## Introduction

Autologging provides two decorators and a metaclass factory:

**`logged`**
decorates a class (or function) to create a `__logger` member.
The logger is automatically named to match the dotted-name of the
containing class or module.
Alternatively, provide a specific logger by passing it to the
decorator (i.e. `logged(my_logger)`).

**`traced`**
decorates a module-level function to provide call/return tracing.
The log record attributes *pathname*, *filename*, *lineno*, *module*,
and *funcName* work as expected (i.e. they refer to the original
function, NOT the proxy function returned by the decorator).

**`TracedMethods`**
creates a metaclass that adds automatic tracing to specified class
methods (just like `traced` does for module-level functions).
The log record attributes *pathname*, *filename*, *lineno*, *module*,
and *funcName* work as expected (i.e. they refer to the original
class method, NOT the proxy method installed by the metaclass).

Additionally, an `autologging.TRACE` (level 1) custom log level is
registered with the Python `logging` module so that tracing messages
can be toggled on/off independently of DEBUG-level logging.

## Installation

[![Wheel Status](https://pypip.in/wheel/Autologging/badge.svg)](https://pypi.python.org/pypi/Autologging/)

The easiest way to install Autologging is to use [pip](https://pip.pypa.io/):

```bash
$ pip install Autologging
```

### Source installation

Clone or fork the repository:

```bash
$ git clone https://github.com/mzipay/Autologging.git
```

Alternatively, download and extract a source _.zip_ or _.tar.gz_ archive from
https://github.com/mzipay/Autologging/releases or
https://pypi.python.org/pypi/Autologging.

Run the test suite and install the `autologging` module:

```bash
$ cd Autologging
$ python setup.py test
$ python setup.py install
```

### Binary installation

Download the Python wheel (_.whl_) or _.egg_ from
https://pypi.python.org/pypi/Autologging, or an _.exe_/_.msi_ Windows installer
from https://sourceforge.net/projects/autologging/files/.

Use [pip](https://pip.pypa.io/) or
[wheel](https://pypi.python.org/pypi/wheel) to install the _.whl_;
[setuptools](https://pypi.python.org/pypi/setuptools) to install an
_.egg_; or run the Windows installer.

