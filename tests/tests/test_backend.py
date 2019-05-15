from django.test import TestCase, override_settings

from drc_cmis.backend import CMISDRCStorageBackend
from drc_cmis.models import DRCCMISConnection

from .factories import (
    DRCCMISConnectionFactory, EnkelvoudigInformatieObjectFactory
)


class CMISStorageTests(TestCase):
    def setUp(self):
        self.backend = CMISDRCStorageBackend()

    def test_get_folder(self):
        self.assertIsNone(self.backend.get_folder("test"))

    def test_create_folder(self):
        self.assertIsNone(self.backend.create_folder("test"))

    def test_rename_folder(self):
        self.assertIsNone(self.backend.rename_folder("test", "new_test"))

    def test_remove_folder(self):
        self.assertIsNone(self.backend.remove_folder("test"))

    def test_get_document_without_cmisstorage(self):
        eio = EnkelvoudigInformatieObjectFactory()
        self.assertIsNone(self.backend.get_document(eio).url)
        self.assertIsNone(self.backend.get_document(eio).auteur)
        self.assertIsNone(self.backend.get_document(eio).bestandsnaam)
        self.assertIsNone(self.backend.get_document(eio).creatiedatum)
        self.assertIsNone(self.backend.get_document(eio).vertrouwelijkheidaanduiding)
        self.assertIsNone(self.backend.get_document(eio).taal)

    def test_get_document(self):
        koppeling = DRCCMISConnectionFactory()
        temp_document = self.backend.get_document(koppeling.enkelvoudiginformatieobject)
        print(temp_document.__dict__)
        self.assertEqual(
            temp_document.url,
            f"http://example.com/cmis/content/{koppeling.enkelvoudiginformatieobject.identificatie}.bin",
        )
        self.assertEqual(temp_document.auteur, '')
        self.assertEqual(temp_document.bestandsnaam, '')
        self.assertEqual(temp_document.creatiedatum, '')
        self.assertEqual(temp_document.vertrouwelijkheidaanduiding, '')
        self.assertEqual(temp_document.taal, '')

    @override_settings(IS_HTTPS=True)
    def test_get_document_https(self):
        koppeling = DRCCMISConnectionFactory()
        temp_document = self.backend.get_document(koppeling.enkelvoudiginformatieobject)
        self.assertEqual(
            temp_document.url,
            f"https://example.com/cmis/content/{koppeling.enkelvoudiginformatieobject.identificatie}.bin",
        )
        self.assertEqual(temp_document.auteur, '')
        self.assertEqual(temp_document.bestandsnaam, '')
        self.assertEqual(temp_document.creatiedatum, '')
        self.assertEqual(temp_document.vertrouwelijkheidaanduiding, '')
        self.assertEqual(temp_document.taal, '')

    def test_create_document(self):
        self.assertEqual(DRCCMISConnection.objects.count(), 0)

        eio = EnkelvoudigInformatieObjectFactory()
        self.backend.create_document(eio)

        self.assertEqual(DRCCMISConnection.objects.count(), 1)
