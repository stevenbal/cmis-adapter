from drc_cmis.client.mapper import DOCUMENT_MAP

from .utils import CMISRequest


class Document:
    def __init__(self, data):
        self.data = data
        self.properties = dict(data.get('properties'))

    def __getattr__(self, name):
        return self.properties.get(DOCUMENT_MAP.get(name), {}).get('value')


class Folder(CMISRequest):
    def __init__(self, data):
        self.data = data
        self.properties = dict(data.get('properties'))

    def __getattr__(self, name):
        return self.properties.get(f"cmis:{name}", {}).get('value')

    def getChildren(self):
        data = {
            "cmisaction": "query",
            "statement": f"SELECT * FROM cmis:folder WHERE IN_FOLDER('{self.objectId}')",
        }
        json_response = self._request(data)
        return self._get_all(json_response, Folder)
