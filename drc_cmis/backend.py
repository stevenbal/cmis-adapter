import base64
import logging

from django.conf import settings
from django.urls import reverse

from cmislib.exceptions import UpdateConflictException
from import_class import import_class

# from .cache import cache
from .client import cmis_client
from .exceptions import DocumentExistsError

logger = logging.getLogger(__name__)


class CMISDRCStorageBackend(import_class(settings.ABSTRACT_BASE_CLASS)):
    """
    This is the backend that is used to store the documents in a CMIS compatible backend.

    This class is based on:
    drc.backend.abstract.BaseDRCStorageBackend
    """
    def create_document(self, validated_data, inhoud):
        identificatie = validated_data.pop('identificatie')
        titel = validated_data.get('titel')

        try:
            cmis_client.create_document(identificatie, validated_data, inhoud)
        except UpdateConflictException:
            raise self.exception_class({None: 'Document is niet uniek. Dit kan liggen aan de titel, inhoud of documentnaam'}, create=True)
        except DocumentExistsError as e:
            raise self.exception_class({None: e.message}, create=True)

    def get_documents(self):
        cmis_documents = cmis_client.get_cmis_documents()

        documents_data = []
        for cmis_doc in cmis_documents:
            dict_document = self._create_dict_from_cmis_doc(cmis_doc)
            if dict_document:
                documents_data.append(dict_document)

        return documents_data

    def update_enkelvoudiginformatieobject(self, validated_data, identificatie, inhoud):
        cmis_client.update_document(identificatie, validated_data, inhoud)

    def get_document(self, uuid):
        cmis_document = cmis_client.get_cmis_document(identificatie=uuid)
        return self._create_dict_from_cmis_doc(cmis_document)

    def _create_dict_from_cmis_doc(self, cmis_doc):
        properties = cmis_doc.getProperties()

        # Values that need some parsing.
        creatiedatum = properties.get("drc:creatiedatum")
        if creatiedatum:
            creatiedatum = creatiedatum.date()

        ontvangstdatum = properties.get("drc:ontvangstdatum")
        if ontvangstdatum:
            ontvangstdatum = ontvangstdatum.date()

        verzenddatum = properties.get("drc:verzenddatum")
        if verzenddatum:
            verzenddatum = verzenddatum.date()

        ondertekening_datum = properties.get("drc:ondertekening_datum")
        if ondertekening_datum:
            ondertekening_datum = ondertekening_datum.date()

        integriteit_datum = properties.get("drc:integriteit_datum")
        if integriteit_datum:
            integriteit_datum = integriteit_datum.date()

        identificatie = properties.get("drc:identificatie")

        try:
            inhoud = base64.b64encode(cmis_doc.getContentStream().read()).decode("utf-8")
        except AssertionError:
            return None
        else:
            return {
                "url": "{}{}".format(settings.HOST_URL, reverse('enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': identificatie})) if identificatie else None,
                "inhoud": "{}{}".format(settings.HOST_URL, reverse('enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': identificatie})),
                "creatiedatum": creatiedatum,
                "ontvangstdatum": ontvangstdatum,
                "verzenddatum": verzenddatum,
                "integriteit_datum": integriteit_datum,
                "ondertekening_datum": ondertekening_datum,
                "titel": properties.get("cmis:name"),
                "identificatie": identificatie,
                "bronorganisatie": properties.get("drc:bronorganisatie"),
                "vertrouwelijkaanduiding": properties.get("drc:vertrouwelijkaanduiding"),
                "auteur": properties.get("drc:auteur"),
                "status": properties.get("drc:status"),
                "beschrijving": properties.get("drc:beschrijving"),
                "indicatie_gebruiksrecht": properties.get("drc:indicatie_gebruiksrecht"),
                "ondertekening_soort": properties.get("drc:ondertekening_soort"),
                "informatieobjecttype": properties.get("drc:informatieobjecttype"),
                "formaat": properties.get("drc:formaat"),
                "taal": properties.get("drc:taal"),
                "bestandsnaam": properties.get("drc:bestandsnaam"),
                "link": properties.get("drc:link"),
                "integriteit_algoritme": properties.get("drc:integriteit_algoritme"),
                "integriteit_waarde": properties.get("drc:integriteit_waarde"),
                "bestandsomvang": len(inhoud),
            }
