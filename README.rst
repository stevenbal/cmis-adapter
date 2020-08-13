===========================
Documenten API CMIS adapter
===========================

:Version: 0.5.0
:Source: https://github.com/open-zaak/cmis-adapter
:Keywords: CMIS, Documenten API, VNG, Common Ground
:PythonVersion: 3.7

|build-status| |coverage| |black| |python-versions| |django-versions| |pypi-version|

A CMIS backend-connector for the `Documenten API`_.

Developed by `Maykin Media B.V.`_ commissioned by the municipality of Utrecht
with support of the municipality of Súdwest-Fryslân and the Open Zaak project
team.


Introduction
============

The Documenten API CMIS adapter allows Django implementations of the Documenten
API to easily connect to a CMIS-compatible Document Management System (DMS).
Most notably it's used by `Open Zaak`_ to use a DMS as backend for the 
Documenten API rather then using its own backend.

Features
--------

Both `CMIS 1.0`_ and `CMIS 1.1`_ are supported but not for all bindings. Below
is a list of supported bindings for each CMIS version.

.. _`CMIS 1.0`: https://docs.oasis-open.org/cmis/CMIS/v1.0/cmis-spec-v1.0.html
.. _`CMIS 1.1`: https://docs.oasis-open.org/cmis/CMIS/v1.1/CMIS-v1.1.html

+----------------------+-----------+-----------+
|                      |  CMIS 1.0 |  CMIS 1.1 |
+======================+===========+===========+
| Web Services binding | Supported |  Untested |
+----------------------+-----------+-----------+
| AtomPub binding      |  Untested |  Untested |
+----------------------+-----------+-----------+
| Browser binding      |    N/A    | Supported |
+----------------------+-----------+-----------+

For the supported bindings, the following features are implemented:

* Retrieve from and store documents in a CMIS-compatible DMS.
* Supports reading and writing of documents.
* Supports checking out/in of documents.
* Supports custom data-model for storing additional meta data.


Installation
============

Requirements
------------

* Python 3.7 or above
* setuptools 30.3.0 or above
* Django 2.2 or newer

Install
-------

1. Install the library in your Django project:

.. code-block:: bash

    $ pip install drc-cmis

2. Add to ``INSTALLED_APPS`` in your Django ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "drc_cmis",
        ...
    ]

3. Create a mapping file to match Documenten API attributes to custom 
   properties in your DMS model. See `Mapping configuration`_.

4. In your ``settings.py``, add these settings to enable it:

.. code-block:: python

    # Enables the CMIS-backend and the Django admin interface for configuring 
    # the DMS settings.
    CMIS_ENABLED = True

    # Absolute path to the mapping of Documenten API attributes to (custom) 
    # properties in your DMS model.
    CMIS_MAPPER_FILE = /path/to/cmis_mapper.json

5. Login to the Django admin as superuser and configure the CMIS backend.

Mapping configuration
=====================

Mapping Documenten API attributes to custom properties in the DMS model should
be done with great care. When the DMS stores these properties, the Documenten 
API relies on their existance to create proper responses.

Below is a snippet of the ``cmis_mapper.json``:

.. code-block:: json

    {
      "DOCUMENT_MAP": {
        "titel": "drc:document__titel"
      }
    }

The ``DOCUMENT_MAP`` describes the mapping for the 
``EnkelvoudigInformatieObject`` resource in the Documenten API. In this 
snippet, only the ``EnkelvoudigInformatieObject.titel`` is mapped to a custom 
DMS property called ``drc:document_titel``.

When creating a document, the custom properties are translated to CMIS 
properties as shown below (note that this is a stripped down request example):

.. code-block:: xml

    <?xml version="1.0"?>
    <soapenv:Envelope xmlmsg:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlmsg:msg="http://docs.oasis-open.org/ns/cmis/messaging/200908/" xmlmsg:core="http://docs.oasis-open.org/ns/cmis/core/200908/">
    <soapenv:Header />
    <soapenv:Body>
      <msg:createDocument>
        <msg:repositoryId>d6a10501-ef36-41e1-9aae-547154f57838</msg:repositoryId>
        <msg:properties>
          <core:propertyString propertyDefinitionId="drc:document__titel">
          <core:value>example.txt</core:value>
        </msg:properties>
        <msg:folderId>workspace://SpacesStore/7c6c7c86-fd63-4eec-bcf8-ffb59f6f6b90</msg:folderId>
      </msg:createDocument>
    </soapenv:Body>
    </soapenv:Envelope>

An example of the mapping configuration, with all possible Documenten API 
resources and attributes is shown in ``test_app/cmis_mapper.json``. The 
related DMS content model for `Alfresco`_ (an open source DMS) is in 
``/alfresco/extension/alfreso-zsdms-model.xml``. Both the mapping and the 
model should be in sync.

In addition to the configurable mapping for ``EnkelvoudigInformatieObject`` 
(``DOCUMENT_MAP``), ``Gebruiksrechten`` (``GEBRUIKSRECHTEN_MAP``) and ``ObjectInformatieObject`` (``OBJECTINFORMATIEOBJECT_MAP``), there are 2 predefined mappings.

Predefined mappings
-------------------

**Zaaktype folder**

Contains all Zaken from this Zaaktype and has itself some meta data about the
Zaaktype. API-attributes are from the `Catalogi API`_ Zaaktype-resource.

.. _`Catalogi API`: https://vng-realisatie.github.io/gemma-zaken/standaard/catalogi/index

``cmis:objectTypeId`` = ``F:drc:zaaktypefolder``

+-------------------+---------------------------------+
| API-attribute     | CMIS-property                   |
+===================+=================================+
| ``url``           | ``drc:zaaktype__url``           |
+-------------------+---------------------------------+
| ``identificatie`` | ``drc:zaaktype__identificatie`` |
+-------------------+---------------------------------+

**Zaak folder**

Contains all Zaak-related documents and has itself some meta data about the
Zaak. API-attributes are from the `Zaken API`_ Zaak-resource.

.. _`Zaken API`: https://vng-realisatie.github.io/gemma-zaken/standaard/zaken/index

``cmis:objectTypeId`` = ``F:drc:zaakfolder``

+---------------------+---------------------------------+
| API-attribute       | CMIS-property                   |
+=====================+=================================+
| ``url``             | ``drc:zaak__url``               |
+---------------------+---------------------------------+
| ``identificatie``   | ``drc:zaak__identificatie``     |
+---------------------+---------------------------------+
| ``zaaktype``        | ``drc:zaak__zaaktypeurl``       |
+---------------------+---------------------------------+
| ``bronorganisatie`` | ``drc:zaak__bronorganisatie``   |
+---------------------+---------------------------------+

Content model configuration
---------------------------

The mapping configuration must match the content model in the DMS. Each 
property, like ``drc:document__titel`` in the example above, must be defined 
in the content model.

The example shown in ``/alfresco/extension/alfreso-zsdms-model.xml`` 
indicates all attributes, types and whether the property is indexed (queryable) 
or not. If these attributes are incorrectly configured, the Documenten API 
might not work correctly.


References
==========

* `Issues <https://github.com/open-zaak/open-zaak/issues>`_
* `Code <https://github.com/open-zaak/cmis-adapter>`_


License
=======

Copyright © Dimpact 2019 - 2020

Licensed under the EUPL_

.. _EUPL: LICENCE.md

.. _`Maykin Media B.V.`: https://www.maykinmedia.nl

.. _`Alfresco`: https://www.alfresco.com/ecm-software/alfresco-community-editions

.. |build-status| image:: https://travis-ci.org/open-zaak/cmis-adapter.svg?branch=master
    :target: https://travis-ci.org/open-zaak/cmis-adapter

.. |coverage| image:: https://codecov.io/gh/open-zaak/cmis-adapter/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/open-zaak/cmis-adapter
    :alt: Coverage status

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/drc-cmis.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/drc-cmis.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/drc-cmis.svg
    :target: https://pypi.org/project/drc-cmis/

.. _Documenten API: https://vng-realisatie.github.io/gemma-zaken/standaard/documenten/index
