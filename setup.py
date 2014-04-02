#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import find_packages, setup

install_requires = []
with open('requirements.txt') as f:
    install_requires = f.read().splitlines()


setup(name='write-it',
    version='0.0.1',
    url='http://writeit.ciudadanointeligente.org',
    author='Fundación Ciudadano Inteligente',
    author_email='lab@ciudadanointeligente.org',
    description="",
    packages=find_packages(exclude=["writeit", "manage", "test"]),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    license='License',
)