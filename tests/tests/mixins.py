from cmislib.exceptions import ObjectNotFoundException

from drc_cmis import settings
from drc_cmis.client import CMISDRCClient


class DMSMixin:
    def setUp(self):
        super().setUp()
        self.cmis_client = CMISDRCClient()
        self.addCleanup(lambda: self._removeTree(f"/{settings.BASE_FOLDER_LOCATION}"))
        self.cmis_client._base_folder = None

    def _removeTree(self, path):
        try:
            root_folder = self.cmis_client._repo.getObjectByPath(path)
        except ObjectNotFoundException:
            return
        except AttributeError:
            return
        root_folder.deleteTree()
