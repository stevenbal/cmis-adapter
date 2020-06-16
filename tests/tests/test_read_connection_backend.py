from io import BytesIO

from django.test import TestCase

from tests.tests.factories import EnkelvoudigInformatieObjectFactory
from tests.tests.mixins import DMSMixin

from drc_cmis.backend import BackendException, CMISDRCStorageBackend
from drc_cmis.client import CMISDRCClient


class CMISReadConnectionTests(DMSMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.backend = CMISDRCStorageBackend()
        self.cmis_client = CMISDRCClient()

    def test_get_document_case_connections(self):
        # Create zaaktype_folder
        zaaktype_folder = self.cmis_client.get_or_create_zaaktype_folder(
            {
                "url": "https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/f7afd156-c8f5-4666-b8b5-28a4a9b5dfc7/zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1",
                "identificatie": 1,
                "omschrijving": "Melding Openbare Ruimte",
            }
        )

        # Create zaak_folder
        self.cmis_client.get_or_create_zaak_folder(
            {
                "url": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid",
                "identificatie": "1bcfd0d6-c817-428c-a3f4-4047038c184d",
                "zaaktype": "https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/f7afd156-c8f5-4666-b8b5-28a4a9b5dfc7/zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1",
                "startdatum": "2023-12-06",
                "einddatum": None,
                "registratiedatum": "2019-04-17",
                "bronorganisatie": "509381406",
            },
            zaaktype_folder,
        )

        # Create document
        eio = EnkelvoudigInformatieObjectFactory(identificatie="test")
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), BytesIO(b"some content"))
        self.assertIsNotNone(document)

        self.backend.create_document_case_connection(
            {"informatieobject": document.url, "object": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid"}
        )

        # Because we need to give alfresco some time to index the document there is a timeout
        import time

        time.sleep(25)

        connections = self.backend.get_document_case_connections()
        self.assertEqual(len(connections), 1)

    def test_get_document_case_connections_without_case_folder(self):
        # Create document
        eio = EnkelvoudigInformatieObjectFactory(identificatie="test")
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), BytesIO(b"some content"))
        self.assertIsNotNone(document)

        self.backend.create_document_case_connection(
            {"informatieobject": document.url, "object": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid"}
        )

        # Because we need to give alfresco some time to index the document there is a timeout
        import time

        time.sleep(25)

        connections = self.backend.get_document_case_connections()
        self.assertEqual(len(connections), 1)

    def test_get_document_case_connections_without_documents(self):
        connections = self.backend.get_document_case_connections()
        self.assertEqual(len(connections), 0)

    def test_get_document_case_connection(self):
        # Create zaaktype_folder
        zaaktype_folder = self.cmis_client.get_or_create_zaaktype_folder(
            {
                "url": "https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/f7afd156-c8f5-4666-b8b5-28a4a9b5dfc7/zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1",
                "identificatie": 1,
                "omschrijving": "Melding Openbare Ruimte",
            }
        )

        # Create zaak_folder
        self.cmis_client.get_or_create_zaak_folder(
            {
                "url": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid",
                "identificatie": "1bcfd0d6-c817-428c-a3f4-4047038c184d",
                "zaaktype": "https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/f7afd156-c8f5-4666-b8b5-28a4a9b5dfc7/zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1",
                "startdatum": "2023-12-06",
                "einddatum": None,
                "registratiedatum": "2019-04-17",
                "bronorganisatie": "509381406",
            },
            zaaktype_folder,
        )

        # Create document
        eio = EnkelvoudigInformatieObjectFactory(identificatie="test")
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), BytesIO(b"some content"))
        self.assertIsNotNone(document)

        self.backend.create_document_case_connection(
            {"informatieobject": document.url, "object": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid"}
        )

        # Because we need to give alfresco some time to index the document there is a timeout
        import time

        time.sleep(25)

        connection = self.backend.get_document_case_connection(document.url.split("/")[-1])
        self.assertIsNotNone(connection)

    def test_get_document_case_connection_without_case_folder(self):
        # Create document
        eio = EnkelvoudigInformatieObjectFactory(identificatie="test")
        eio_dict = eio.__dict__

        document = self.backend.create_document(eio_dict.copy(), BytesIO(b"some content"))
        self.assertIsNotNone(document)

        self.backend.create_document_case_connection(
            {"informatieobject": document.url, "object": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/random-zaak-uuid"}
        )

        # Because we need to give alfresco some time to index the document there is a timeout
        import time

        time.sleep(25)

        connection = self.backend.get_document_case_connection(document.url.split("/")[-1])
        self.assertIsNotNone(connection)

    def test_get_document_case_connection_without_documents(self):
        with self.assertRaises(BackendException):
            self.backend.get_document_case_connection("some_identifier")
