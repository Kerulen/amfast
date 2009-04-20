import os
from setuptools import setup, find_packages

from distutils.core import setup, Extension

extensions = [
    Extension('amfast.encode',
        sources = [os.path.join('amfast', 'ext_src', 'encoder.c')]),
    Extension('amfast.decode',
        sources = [os.path.join('amfast', 'ext_src', 'decoder.c')]),
    Extension('amfast.buffer',
        sources = [os.path.join('amfast', 'ext_src', 'buffer.c')]),
    Extension('amfast.context',
        sources = [os.path.join('amfast', 'ext_src', 'context.c')])
    ]

setup(name="AmFast",
    version = "0.3.0",
    description = "A C extension to encode/decode Python objects with AMF0 and AMF3. Includes support for NetConnection, RemoteObject, IExternizeable, and custom type serialization.",
    url = "http://code.google.com/p/amfast/",
    author = "Dave Thompson",
    author_email = "dthomp325@gmail.com",
    maintainer = "Dave Thompson",
    maintainer_email = "dthomp325@gmail.com",
    keywords = "amf amf0 amf3 flash flex pyamf",
    platforms = ["any"],
    test_suite = "tests.suite",
    packages = ['amfast', 'amfast.class_def', 'amfast.remoting'],
    ext_modules = extensions,
    classifiers = [
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities"
    ])
