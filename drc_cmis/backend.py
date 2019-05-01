from django.urls import reverse

from drc.backend.abstract import BaseDRCStorageBackend

from drc_cmis import settings

from .client import default_client


class CMISDRCStorageBackend(BaseDRCStorageBackend):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.
    """

    def get_folder(self, zaak_url):
        # Folders will not be supported for now
        pass

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
            enkelvoudiginformatieobject.koppeling
        except AttributeError:
            return None
        else:
            return reverse('cmis:cmis-document-download', kwargs={'inhoud': enkelvoudiginformatieobject.identificatie})

    def create_document(self, enkelvoudiginformatieobject, bestand=None, link=None):
        from .models import DRCCMISConnection
        connection = DRCCMISConnection.objects.create(
            enkelvoudiginformatieobject=enkelvoudiginformatieobject, cmis_object_id=""
        )

        cmis_doc = default_client.maak_zaakdocument_met_inhoud(
            koppeling=connection,
            zaak_url=None,
            filename=None,
            sender=settings.DRC_CMIS_SENDER_PROPERTY,
            stream=bestand,
        )
        connection.cmis_object_id = cmis_doc.getObjectId().rsplit(";")[0]
        connection.save()

    def update_document(self, enkelvoudiginformatieobject, updated_values, bestand=None, link=None):
        if not hasattr(enkelvoudiginformatieobject, 'cmisstorage'):
            raise AttributeError('This document is not connected to CMIS')
        default_client.update_zaakdocument(enkelvoudiginformatieobject.cmisstorage)

    def remove_document(self, enkelvoudiginformatieobject):
        raise NotImplementedError()

    def move_document(self, enkelvoudiginformatieobject):
        raise NotImplementedError()
