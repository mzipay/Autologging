# -*- coding: utf-8 -*-

# Copyright (c) 2013 Matthew Zipay <mattz@ninthtest.net>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Example functions that have been decorated with
:func:`autologging.logged`.

"""

__author__ = "Simon Knopp <simon.knopp@pg.canterbury.ac.nz>"
__version__ = "0.1"

import logging

from autologging import logged


@logged
def module_logger_fn():
    """Uses the default (module) logger."""
    module_logger_fn.__logger.info("module_logger_fn test.")


_named_logger = logging.getLogger("logged.testing")


@logged(_named_logger)
def named_logger_fn():
    """"Uses a specifically-named logger."""
    named_logger_fn.__logger.info( "named_logger_fn test.")


def outer_fn():
    """Test a logged nested function."""

    @logged
    def inner_fn():
        return inner_fn.__logger.name

    return inner_fn


@logged
def _internal_fn():
    """Test an internal-named function and nested function."""

    @logged
    def _inner_internal_fn():
        return _inner_internal_fn.__logger.name

    return _inner_internal_fn
