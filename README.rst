==============
gemma-drc-cmis
==============

.. .. image:: https://img.shields.io/pypi/v/drc-cmis.svg?style=for-the-badge
..         :target: https://pypi.org/project/drc-cmis/

.. .. image:: https://img.shields.io/travis/GemeenteUtrecht/gemma-drc-cmis.svg?style=for-the-badge
..         :target: https://travis-ci.org/GemeenteUtrecht/gemma-drc-cmis

A CMIS backend for gemma-documentregistratiecomponent


* Free software: MIT license
* Documentation: https://drc-cmis.readthedocs.io.

How to install
--------------

Install via pip

::

    pip install gemma-drc-cmis

Add to installed apps

::

    INSTALLED_APPS = [
        ...
        'drc_cmis',
        ...
    ]

Enable `cmis storage` in the admin of the drc under `Plugin` `Storage Config`.

Features
--------

- Integrate cmis in the drc
