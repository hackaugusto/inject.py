# -*- coding: utf-8 -*-
import sys

from setuptools import setup
from setuptools.command.test import test

class Tox(test):
    def initialize_options(self):
        test.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        sys.exit(tox.cmdline())

setup(
    name='inject.py',
    version='0.1',
    description='Inject is a simple function that uses values from a dictionary as arguments for a function.',
    url='https://github.com/hackaugusto/inject.py',
    author='Augusto F. Hack',
    author_email='hack.augusto@gmail.com',
    license='MIT',

    py_modules=['inject'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    keywords=['inject', 'function', 'arguments'],
    tests_require=['tox'],
    cmdclass={'test': Tox},
)

