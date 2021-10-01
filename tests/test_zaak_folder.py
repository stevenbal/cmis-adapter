import io
import os
from unittest import skipIf

from django.test import TestCase

from drc_cmis.models import CMISConfig, UrlMapping
from drc_cmis.webservice.drc_document import Document

from .mixins import DMSMixin

CMIS_CACHE_CONFIGURED = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "cmis-client": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}
CMIS_CACHE_NOT_CONFIGURED = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}


BASE_DOCUMENT_URL = "https://openzaak.nl/documenten/api/v1/"
DOCUMENT = {
    "bronorganisatie": "159351741",
    "creatiedatum": "2020-01-01T00:00:00+01:00",
    "titel": "detailed summary",
    "auteur": "test_auteur",
    "formaat": "txt",
    "taal": "eng",
    "bestandsnaam": "dummy.txt",
    "link": "https://drc.utrechtproeftuin.nl/api/v1/enkelvoudiginformatieobjecten/d06f86e0-1c3a-49cf-b5cd-01c079cf8147/download",
    "beschrijving": "test_beschrijving",
    "vertrouwelijkheidaanduiding": "openbaar",
}

BASE_ZAAKTYPE_URL = "https://openzaak.nl/catalogi/api/v1/"
ZAAKTYPE = {
    "url": f"{BASE_ZAAKTYPE_URL}zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1",
    "identificatie": 1,
    "omschrijving": "Melding Openbare Ruimte",
}

BASE_ZAAK_URL = "https://openzaak.nl/zaken/api/v1/"
ZAAK = {
    "url": f"{BASE_ZAAK_URL}zaken/1c8e36be-338c-4c07-ac5e-1adf55bec04a",
    "identificatie": "1bcfd0d6-c817-428c-a3f4-4047038c184d",
    "zaaktype": f"{BASE_ZAAKTYPE_URL}zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1",
    "startdatum": "2023-12-06",
    "einddatum": None,
    "registratiedatum": "2019-04-17",
    "bronorganisatie": "509381406",
}


class CMISZaakFolderTests(DMSMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        config = CMISConfig.get_solo()

        UrlMapping.objects.create(
            long_pattern="https://openzaak.utrechtproeftuin.nl/zaken",
            short_pattern="https://zak.nl",
            config=config,
        )
        UrlMapping.objects.create(
            long_pattern="https://openzaak.utrechtproeftuin.nl/catalogi",
            short_pattern="https://cat.nl",
            config=config,
        )

    @skipIf(
        os.getenv("CMIS_BINDING") != "WEBSERVICE",
        "Not implemented in browser binding.",
    )
    def test_get_children_documents(self):
        document = self.cmis_client.create_document(
            identification="64d15843-1990-4af2-b6c8-d5a0be52402f",
            data=DOCUMENT,
            content=io.BytesIO(b"some file content"),
            bronorganisatie="159351741",
        )
        document_url = (
            f"{BASE_DOCUMENT_URL}enkelvoudiginformatieobjecten/{document.uuid}"
        )

        oio = {
            "object": ZAAK["url"],
            "informatieobject": document_url,
            "object_type": "zaak",
        }
        self.cmis_client.create_oio(
            oio_data=oio, zaak_data=ZAAK, zaaktype_data=ZAAKTYPE
        )

        zaak_folder = self.cmis_client.query(
            self.cmis_client.zaakfolder_type.type_name,
            lhs=["drc:zaak__url = '%s'"],
            rhs=[ZAAK["url"]],
        )[0]

        documents = zaak_folder.get_children_documents()

        self.assertEqual(1, len(documents))
        self.assertTrue(isinstance(documents[0], Document))

        documents_data = zaak_folder.get_children_documents(
            convert_to_document_type=False
        )

        self.assertEqual(1, len(documents_data))
        self.assertTrue(isinstance(documents_data[0], dict))
