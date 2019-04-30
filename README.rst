==============
gemma-drc-cmis
==============


.. .. image:: https://img.shields.io/pypi/v/drc_cmis.svg
..         :target: https://pypi.python.org/pypi/drc_cmis

.. .. image:: https://img.shields.io/travis/audreyr/drc_cmis.svg
..         :target: https://travis-ci.org/audreyr/drc_cmis

.. .. image:: https://readthedocs.org/projects/drc-cmis/badge/?version=latest
..         :target: https://drc-cmis.readthedocs.io/en/latest/?badge=latest
..         :alt: Documentation Status

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

Add `drc_cmis` to the backends

::

    DRC_STORAGE_BACKENDS = [
        'drc.backend.django.DjangoDRCStorageBackend', # If you also want to store it via django.
        'drc_cmis.backend.CMISDRCStorageBackend',
    ]


Features
--------

- Integrate cmis with the issues
- Issues all year round
