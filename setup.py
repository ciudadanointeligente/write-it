#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

install_requires = ['Django',
'django-plugins',
'python-mimeparse',
'django-tastypie==0.13.3',
'email_reply_parser',
'flufl.bounce',
'django-markdown-deux',
'requests',
'django-extensions',
'django-haystack',
'pyelasticsearch',
'celery',
'pyyaml',
'django-celery',
'django-autoslug',
'pytz>=2013b',
'popit-django',
'django-admin-bootstrapped',
'django-object-actions',
'unidecode']


setup(
    name='write-it',
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
