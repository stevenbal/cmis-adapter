import logging

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from .client import default_client

logger = logging.getLogger(__name__)


class CMISDRCStorageBackend:
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
        try:
            enkelvoudiginformatieobject.cmisstorage
        except ObjectDoesNotExist:
            # logger.exception(e)
            return None
        else:
            path = reverse('cmis:cmis-document-download', kwargs={'inhoud': enkelvoudiginformatieobject.identificatie})
            host = get_current_site(None).domain
            schema = 'https' if settings.IS_HTTPS else 'http'
            url = f'{schema}://{host}{path}'
            return url

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
