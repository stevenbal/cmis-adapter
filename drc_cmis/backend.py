import logging

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

from import_class import import_class

# from .cache import cache
from .client import default_client
from .exceptions import DocumentDoesNotExistError

logger = logging.getLogger(__name__)


class CMISDRCStorageBackend(import_class(settings.ABSTRACT_BASE_CLASS)):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.

    This class is based on:
    drc.backend.abstract.BaseDRCStorageBackend
    """

    def get_folder(self, zaak_url):
        # Folders will not be supported for now
        return None

    def create_folder(self, zaak_url):
        # Folders will not be supported for now
        pass

    def rename_folder(self, old_zaak_url, new_zaak_url):
        # Folders will not be supported for now
        pass

    def remove_folder(self, zaak_url):
        # Folders will not be supported for now
        pass

    def get_document(self, enkelvoudiginformatieobject):
        TempDocument = import_class(settings.TEMP_DOCUMENT_CLASS)
        try:
            storage = enkelvoudiginformatieobject.cmisstorage
        except AttributeError:
            # logger.exception(e)
            return TempDocument()
        else:
            cached_document = cache.get(enkelvoudiginformatieobject.identificatie)
            if cached_document:
                return cached_document

            print('creating caches')
            try:
                cmis_doc = default_client._get_cmis_doc(enkelvoudiginformatieobject)
            except DocumentDoesNotExistError:
                temp_document = TempDocument()
                cache.set(enkelvoudiginformatieobject.identificatie, temp_document, 60)
                return temp_document
            else:
                temp_document = TempDocument(
                    url=reverse('cmis:cmis-document-download', kwargs={'inhoud': enkelvoudiginformatieobject.identificatie}),
                    auteur=cmis_doc.properties.get('zsdms:documentauteur'),
                    bestandsnaam=cmis_doc.properties.get('cmis:name'),
                    creatiedatum=cmis_doc.properties.get('zsdms:documentcreatiedatum'),
                    vertrouwelijkheidaanduiding=cmis_doc.properties.get('zsdms:vertrouwelijkaanduiding'),
                    taal=cmis_doc.properties.get('zsdms:documenttaal'),
                )
                cache.set(enkelvoudiginformatieobject.identificatie, temp_document, 60)
                return temp_document


    def create_document(self, enkelvoudiginformatieobject, bestand=None, link=None):
        from .models import DRCCMISConnection, CMISConfiguration
        connection = DRCCMISConnection.objects.create(
            enkelvoudiginformatieobject=enkelvoudiginformatieobject, cmis_object_id=""
        )

        config = CMISConfiguration.get_solo()
        cmis_doc = default_client.maak_zaakdocument_met_inhoud(
            koppeling=connection,
            zaak_url=None,
            filename=None,
            sender=config.sender_property,
            stream=bestand,
        )
        connection.cmis_object_id = cmis_doc.getObjectId().rsplit(";")[0]
        connection.save()

    def update_document(self, enkelvoudiginformatieobject, updated_values, bestand=None, link=None):
        if not hasattr(enkelvoudiginformatieobject, 'cmisstorage'):
            raise AttributeError('This document is not connected to CMIS')
        default_client.update_zaakdocument(enkelvoudiginformatieobject.cmisstorage)

    def remove_document(self, enkelvoudiginformatieobject):
        if not hasattr(enkelvoudiginformatieobject, 'cmisstorage'):
            raise AttributeError('This document is not connected to CMIS')
        default_client.gooi_in_prullenbak(enkelvoudiginformatieobject)

    def connect_document_to_folder(self, enkelvoudiginformatieobject):
        # Folders will not be supported for now
        # Alfresco does not support multiple connections yet.
        # TODO: Look into relationships
        # createRelationship
        pass
