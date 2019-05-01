===================
Alfresco on Docker
===================

Creates a container that runs Alfresco Community.

Usage
=====

To use this with your project you need to follow these steps:

#. Go to this directory::

    $ cd alfresco

#. Run docker-compose in the background::

    $ docker-compose up -d

#. If this is the first time, it will take a while for Alfresco to be
   downloaded, installed and configured.

#. Navigate to ``http://localhost:8080/share/page/context/mine/myfiles``.

#. In the UI, navigate to: Data ``Dictionary`` > ``Models``

#. Locate the ``alfresco-zsdms-model.xml`` in this folder and upload it.

#. After upload, hover over the file and on the right side click
   "Eigenschappen bewerken"

#. Find "Model Active" and make sure the checkbox is checked.

#. Click "Opslaan".

Locations
=========

#. You can find the Alfresco installation at::

    http://localhost:8080/
    # The default username/password are: admin/admin

#. You can find the CMIS endpoint at::

    http://localhost:8082/alfresco/cmisatom
