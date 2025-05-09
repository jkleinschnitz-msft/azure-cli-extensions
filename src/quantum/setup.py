#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from codecs import open
from setuptools import setup, find_packages
try:
    from azure_bdist_wheel import cmdclass
except ImportError:
    from distutils import log as logger
    logger.warn("Wheel is not available, disabling bdist_wheel hook")

# This version should match the latest entry in HISTORY.rst
# Also, when updating this, please review the version used by the extension to
# submit requests, which can be found at './azext_quantum/__init__.py'
VERSION = '1.0.0b6'

# The full list of classifiers is available at
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'License :: OSI Approved :: MIT License',
]

with open('README.rst', 'r', encoding='utf-8') as f:
    README = f.read()
with open('HISTORY.rst', 'r', encoding='utf-8') as f:
    HISTORY = f.read()

setup(
    name='quantum',
    version=VERSION,
    description='Microsoft Azure Command-Line Tools Quantum Extension',
    author='Microsoft Corporation, Quantum Team',
    author_email='que-contacts@microsoft.com',
    url='https://github.com/Azure/azure-cli-extensions/tree/main/src/quantum',
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    package_data={'azext_quantum': ['azext_metadata.json', 'operations/templates/create-workspace-and-assign-role.json']},
)
