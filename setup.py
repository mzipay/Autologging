# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="Autologging",
    version="1.2.0",
    description="Autologging makes logging and tracing Python classes easy.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matthew Zipay",
    author_email="mattz@ninthtest.info",
    url="http://ninthtest.info/python-autologging/",
    download_url = "https://sourceforge.net/projects/autologging/files/",
    py_modules=["autologging"],
    test_suite="test.suite",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: Stackless",
        "Programming Language :: Python :: Implementation :: Jython",
        "Programming Language :: Python :: Implementation :: IronPython",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    license="MIT License",
    keywords=["logging", "tracing"]
)

