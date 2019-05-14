#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["django_choices", "django", "cmislib-maykin", "django-solo"]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="maykinmedia",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: Django",
    ],
    description="A CMIS backend for gemma-documentregistratiecomponent",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="drc_cmis",
    name="drc_cmis",
    packages=find_packages(include=["drc_cmis"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/gemeenteutrecht/drc_cmis",
    version="0.0.6",
    zip_safe=False,
)
