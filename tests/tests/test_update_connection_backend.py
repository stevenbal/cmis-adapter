from io import BytesIO

from django.test import TestCase

from tests.tests.factories import EnkelvoudigInformatieObjectFactory
from tests.tests.mixins import DMSMixin

from drc_cmis import settings
from drc_cmis.backend import BackendException, CMISDRCStorageBackend
from drc_cmis.models import CMISConfig, CMISFolderLocation


class CMISReadConnectionTests(DMSMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.backend = CMISDRCStorageBackend()
        location = CMISFolderLocation.objects.create(location=settings.BASE_FOLDER_LOCATION)
        config = CMISConfig.get_solo()
        config.locations.add(location)

    def test_update_document_case_connection_no_document(self):
        with self.assertRaises(BackendException):
            self.backend.update_document_case_connection("some data", {})

    def test_update_document_case_connection(self):
        # Create document
        eio = EnkelvoudigInformatieObjectFactory()
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), None)
        self.assertIsNotNone(document)

        connection = self.backend.create_document_case_connection(
            {"informatieobject": document.url, "object": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid"}
        )
        self.assertEqual(connection.object, "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid")
        self.assertIsNone(connection.object_type)
        self.assertIsNone(connection.aard_relatie)
        self.assertIsNone(connection.titel)
        self.assertIsNone(connection.beschrijving)
        self.assertIsNotNone(connection.registratiedatum)

        connection_update = self.backend.update_document_case_connection(
            document.url.split("/")[-1], {"titel": "dit is een nieuwe titel"}
        )
        self.assertEqual(connection_update.object, "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid")
        self.assertIsNone(connection_update.object_type)
        self.assertIsNone(connection_update.aard_relatie)
        self.assertEqual(connection_update.titel, "dit is een nieuwe titel")
        self.assertIsNone(connection_update.beschrijving)
        self.assertIsNotNone(connection.registratiedatum)
