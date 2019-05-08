from django.test import TestCase

from drc_cmis.backend import CMISDRCStorageBackend

from .factories import EnkelvoudigInformatieObjectFactory


class CMISStorageTests(TestCase):
    def setUp(self):
        self.backend = CMISDRCStorageBackend()

    def test_get_folder(self):
        self.assertIsNone(self.backend.get_folder('test'))

    def test_create_folder(self):
        self.assertIsNone(self.backend.create_folder('test'))

    def test_rename_folder(self):
        self.assertIsNone(self.backend.rename_folder('test', 'new_test'))

    def test_remove_folder(self):
        self.assertIsNone(self.backend.remove_folder('test'))

    def test_get_document_without_cmisstorage(self):
        eio = EnkelvoudigInformatieObjectFactory()
        self.assertIsNone(self.backend.get_document(eio))
