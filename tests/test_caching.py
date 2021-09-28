import io
import os
from unittest import skipIf
from unittest.mock import patch

from django.core.cache import caches
from django.test import TestCase, override_settings

from drc_cmis.webservice.client import SOAPCMISClient

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


@skipIf(
    os.getenv("CMIS_BINDING") != "WEBSERVICE",
    "Browser binding doesn't support caching",
)
@override_settings(CACHES=CMIS_CACHE_CONFIGURED)
class CMISClientCacheTests(DMSMixin, TestCase):
    def test_filtering_oios_caches_documents(self):
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

        self.cmis_client.filter_oios(lhs=["drc:oio__zaak = '%s'"], rhs=[ZAAK["url"]])

        cache = caches["cmis-client"]
        self.assertIsNotNone(cache.get(document.uuid))

    def test_retrieving_documents_by_uuid_uses_cache(self):
        document = self.cmis_client.create_document(
            identification="64d15843-1990-4af2-b6c8-d5a0be52402f",
            data=DOCUMENT,
            content=io.BytesIO(b"some file content"),
            bronorganisatie="159351741",
        )

        cache = caches["cmis-client"]
        cache.set(document.uuid, document.properties)

        with patch.object(SOAPCMISClient, "request") as m:
            self.cmis_client.query(
                return_type_name="document",
                lhs=["drc:document__uuid = '%s'"],
                rhs=[document.uuid],
            )

            m.assert_not_called()

    @override_settings(CACHES=CMIS_CACHE_NOT_CONFIGURED)
    def test_cache_not_configured(self):
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

        with patch.object(SOAPCMISClient, "cache_related_documents") as m:
            self.cmis_client.filter_oios(
                lhs=["drc:oio__zaak = '%s'"], rhs=[ZAAK["url"]]
            )

            m.assert_not_called()

    def test_no_documents_related_to_case(self):
        with patch.object(SOAPCMISClient, "request") as m:
            self.cmis_client.cache_related_documents(oios=[])

            m.assert_not_called()
