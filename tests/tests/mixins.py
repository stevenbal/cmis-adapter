from django.test import override_settings

from cmislib.exceptions import ObjectNotFoundException

from drc_cmis import settings
from drc_cmis.client import default_client


class DMSMixin:
    @override_settings(DRC_CMIS_TEMP_FOLDER_NAME='/_temp')
    def setUp(self):
        super().setUp()

        self.cmis_client = default_client
        self.addCleanup(lambda: self._removeTree('/Zaken'))
        self.addCleanup(lambda: self._removeTree('/Sites/archief/documentLibrary'))
        self.addCleanup(lambda: self._removeTree('/_temp'))
        self.addCleanup(lambda: self._removeTree('/Unfiled'))
        self.addCleanup(lambda: self._removeTree('/enkelvoudiginformatieobjecten'))

        self.zaak_url = 'http://zaak.nl/locatie'

    def _removeTree(self, path):
        try:
            root_folder = self.cmis_client._repo.getObjectByPath(path)
        except ObjectNotFoundException:
            return
        root_folder.deleteTree()

    def assertExpectedProps(self, obj, expected: dict):
        for prop, expected_value in expected.items():
            with self.subTest(prop=prop, expected_value=expected_value):
                self.assertEqual(obj.properties[prop], expected_value, msg="prop: {}".format(prop))
