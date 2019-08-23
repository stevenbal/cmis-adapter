import base64
import mimetypes
from datetime import date, datetime
from io import StringIO

from drc_cmis.client.mapper import DOCUMENT_MAP

from .utils import CMISRequest


class Document(CMISRequest):
    def __init__(self, data):
        self.data = data
        self.properties = dict(data.get('properties'))
        self.setup()

    def __getattr__(self, name):
        return self.properties.get(DOCUMENT_MAP.get(name, f"cmis:{name}"), {}).get('value')

    def checkout(self):
        props = {"objectId": self.objectId, "cmisaction": "checkOut"}
        # print(self.root_url)
        self.setup()
        json_response = self._request(props, self.root_url)
        return Document(json_response)

    def reload(self, **kwargs):
        if self._extArgs:
            self._extArgs.update(kwargs)
        else:
            self._extArgs = kwargs

        self.setup()
        url = f"{self.root_url}?objectId={self.objectId}&cmisselector=object"
        json_response = self._get(url)
        self.data = json_response
        self.properties = json_response.get('properties')

    def update_properties(self, properties):
        # get the root folder URL
        updateUrl = f"{self.root_url}?objectId={self.objectId}"

        props = {"cmisaction": "update"}

        propCount = 0
        for prop_key, prop_value in properties.items():
            # Skip property because update is not allowed
            if prop_key == 'cmis:objectTypeId':
                continue

            if isinstance(prop_value, date):
                prop_value = prop_value.strftime('%Y-%m-%dT%H:%I:%S.000Z')

            props["propertyId[%s]" % propCount] = prop_key
            props["propertyValue[%s]" % propCount] = prop_value
            propCount += 1

        # invoke the URL
        json_response = self._request(props, updateUrl)
        self.data = json_response
        self.properties = json_response.get('properties')

        return self

    def checkin(self, checkinComment, major=True):
        props = {
            "objectId": self.objectId,
            "cmisaction": "checkIn",
            "checkinComment": checkinComment,
            "major": major,
        }

        # invoke the URL
        json_response = self._request(props, self.root_url)
        return Document(json_response)

    def setContentStream(self, content_file):
        url = self.root_url
        data = {
            "objectId": self.objectId,
            "cmisaction": "setContent",
        }

        mimetype = None
        # need to determine the mime type
        if not mimetype and hasattr(content_file, 'name'):
            mimetype, _encoding = mimetypes.guess_type(content_file.name)

        if not mimetype:
            mimetype = 'application/binary'

        files = {self.name: (self.name, content_file, mimetype)}

        json_response = self._request(data, url, files=files)

        return Document(json_response)

    def getContentStream(self):
        data = {
            "objectId": self.objectId,
            "cmisaction": "content",
        }
        self.setup()
        json_response = self._get(self.root_url, data)
        return StringIO(json_response)


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

    def createFolder(self, name, properties={}, **kwargs):
        props = {"objectId": self.objectId,
                 "cmisaction": "createFolder",
                 "propertyId[0]": "cmis:name",
                 "propertyValue[0]": name}

        props["propertyId[1]"] = "cmis:objectTypeId"
        if 'cmis:objectTypeId' in properties.keys():
            props["propertyValue[1]"] = properties['cmis:objectTypeId']
        else:
            props["propertyValue[1]"] = "cmis:folder"

        prop_count = 2
        for prop in properties:
            props[f"propertyId[{prop_count}]"] = prop.key
            props[f"propertyValue[{prop_count}]"] = prop
            prop_count += 1

        json_response = self._request(props, self.root_url)
        return Folder(json_response)

    def create_document(self, name, properties, content_file=None, **kwargs):
        props = {"objectId": self.objectId,
                 "cmisaction": "createDocument",
                 "propertyId[0]": "cmis:name",
                 "propertyValue[0]": name}

        props["propertyId[1]"] = "cmis:objectTypeId"
        if 'cmis:objectTypeId' in properties.keys():
            props["propertyValue[1]"] = properties['cmis:objectTypeId']
        else:
            props["propertyValue[1]"] = "drc:document"

        prop_count = 2
        for prop_key, prop_value in properties.items():
            if isinstance(prop_value, date):
                prop_value = prop_value.strftime('%Y-%m-%dT%H:%I:%S.000Z')

            props[f"propertyId[{prop_count}]"] = prop_key
            props[f"propertyValue[{prop_count}]"] = prop_value
            prop_count += 1

        mimetype = None
        # need to determine the mime type
        if not mimetype and hasattr(content_file, 'name'):
            mimetype, _encoding = mimetypes.guess_type(content_file.name)

        if not mimetype:
            mimetype = 'application/binary'

        files = {name: (name, content_file, mimetype)}

        json_response = self._request(props, self.root_url, files=files)
        return Folder(json_response)
