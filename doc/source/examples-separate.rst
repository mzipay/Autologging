===============================================
Separate configurations for logging and tracing
===============================================

:Release: |release|

The purpose of logging is to capture information (caught errors,
branching decisions, calculation results, etc.).

The purpose of tracing is to capture program flow and data (which
functions and methods are called, in what sequence, and with what
parameters).

In addition to serving different purposes, logging and tracing
typically have different intended audiences. While logging output is
generally useful for *anyone* who must observe an application
(developers as well as QA testers, administrators, business analysts,
etc.), tracing is of use primarily for developers.

Because the purpose of and audience for logging and tracing differ, it
is often convenient to configure and control them separately. This may
include, but is not limited to:

* being able to enable/disable logging and tracing independent of one
  another
* writing logging output and tracing output to different log files
* using different log entry formatting for logging and tracing

Standard Python :mod:`logging` configuration can be used in combination
with Autologging to accomplish these goals.

In the example module below, we have logged and traced a simple class::

   # my_module.py

   import logging

   from autologging import logged, traced


   @traced
   @logged
   class MyClass:

      def my_method(self, arg, keyword=None):
         if keyword is not None:
            self.__log.debug("taking the keyword branch")
            return "{} and {}".format(arg, keyword)
         return arg.upper()

We will now configure the logging system to write *two* log files -
one that contains all log entries (including tracing), and another that
contains **only** non-tracing log entries::

   # my_module_main.py

   import logging
   import logging.config

   import autologging

   from my_module import MyClass

   logging.config.dictConfig({
       "version": 1,
       "formatters": {
           "logformatter": {
               "format":
                   "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s",
           },
           "traceformatter": {
               "format":
                   "%(asctime)s:%(process)s:%(levelname)s:%(filename)s:"
                       "%(lineno)s:%(name)s:%(funcName)s:%(message)s",
           },
       },
       "handlers": {
           "loghandler": {
               "class": "logging.FileHandler",
               "level": logging.DEBUG,
               "formatter": "logformatter",
               "filename": "app.log",
           },
           "tracehandler": {
               "class": "logging.FileHandler",
               "level": autologging.TRACE,
               "formatter": "traceformatter",
               "filename": "trace.log",
           },
       },
       "loggers": {
           "my_module.MyClass": {
               "level": autologging.TRACE,
               "handlers": ["tracehandler", "loghandler"],
           },
       },
   })

   if __name__ == "__main__":
       obj = MyClass()
       obj.my_method("test")
       obj.my_method("spam", keyword="eggs")

If we now run the application, it will produce two log files ("app.log"
and "trace.log").

The "app.log" file contains the single DEBUG record::

   2016-01-17 19:58:52,639:DEBUG:my_module.MyClass:my_method:taking the keyword branch

The "trace.log" file contains call and return tracing for both method
calls as well as the DEBUG record::

   2016-01-17 19:58:52,639:24100:TRACE:my_module.py:12:my_module.MyClass:my_method:CALL *('test',) **{}
   2016-01-17 19:58:52,639:24100:TRACE:my_module.py:16:my_module.MyClass:my_method:RETURN 'TEST'
   2016-01-17 19:58:52,639:24100:TRACE:my_module.py:12:my_module.MyClass:my_method:CALL *('spam',) **{'keyword': 'eggs'}
   2016-01-17 19:58:52,639:24100:DEBUG:my_module.py:14:my_module.MyClass:my_method:taking the keyword branch
   2016-01-17 19:58:52,639:24100:TRACE:my_module.py:16:my_module.MyClass:my_method:RETURN 'spam and eggs'

Many other configurations are possible using various combinations of
:mod:`logging.config` settings and/or explicitly-named trace loggers
via :func:`autologging.traced`.

