import mimetypes
from datetime import date
from io import BytesIO

from drc_cmis.client.mapper import DOCUMENT_MAP

from .utils import CMISRequest


class CMISBaseObject(CMISRequest):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.properties = dict(data.get('properties'))

    def reload(self):
        params = {
            "objectId": self.objectId,
            "cmisselector": "object",
        }

        json_response = self.get_request(self.root_folder_url, params=params)
        self.data = json_response
        self.properties = json_response.get('properties')

    def get_object_parents(self):
        params = {
            "objectId": self.objectId,
            "cmisselector": "parents",
        }

        json_response = self.get_request(self.root_folder_url, params=params)
        return self.get_all_objects(json_response, Folder)


class Document(CMISBaseObject):
    def __getattr__(self, name):
        return self.properties.get(DOCUMENT_MAP.get(name, f"cmis:{name}"), {}).get('value')

    def checkout(self):
        data = {"objectId": self.objectId, "cmisaction": "checkOut"}
        json_response = self.post_request(self.root_folder_url, data=data)
        return Document(json_response)

    def update_properties(self, properties):
        data = {
            "objectId": self.objectId,
            "cmisaction": "update",
        }

        prop_count = 0
        for prop_key, prop_value in properties.items():
            # Skip property because update is not allowed
            if prop_key == 'cmis:objectTypeId':
                continue

            if isinstance(prop_value, date):
                prop_value = prop_value.strftime('%Y-%m-%dT%H:%I:%S.000Z')

            data["propertyId[%s]" % prop_count] = prop_key
            data["propertyValue[%s]" % prop_count] = prop_value
            prop_count += 1

        # invoke the URL
        json_response = self.post_request(self.root_folder_url, data=data)
        self.data = json_response
        self.properties = json_response.get('properties')

        return self

    def checkin(self, checkin_comment, major=True):
        props = {
            "objectId": self.objectId,
            "cmisaction": "checkIn",
            "checkinComment": checkin_comment,
            "major": major,
        }

        # invoke the URL
        json_response = self.post_request(self.root_folder_url, props)
        return Document(json_response)

    def set_content_stream(self, content_file):
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

        json_response = self.post_request(self.root_folder_url, data=data, files=files)
        return Document(json_response)

    def get_content_stream(self):
        params = {
            "objectId": self.objectId,
            "cmisaction": "content",
        }
        json_response = self.get_request(self.root_folder_url, params=params)
        return BytesIO(json_response.encode('utf-8'))


class Folder(CMISBaseObject):
    def __getattr__(self, name):
        return self.properties.get(f"cmis:{name}", {}).get('value')

    def get_children(self):
        data = {
            "cmisaction": "query",
            "statement": f"SELECT * FROM cmis:folder WHERE IN_FOLDER('{self.objectId}')",
        }
        json_response = self.post_request(self.base_url, data=data)
        return self.get_all_resutls(json_response, Folder)

    def create_folder(self, name, properties={}, **kwargs):
        data = {
            "objectId": self.objectId,
            "cmisaction": "createFolder",
            "propertyId[0]": "cmis:name",
            "propertyValue[0]": name
        }

        data["propertyId[1]"] = "cmis:objectTypeId"
        if 'cmis:objectTypeId' in properties.keys():
            data["propertyValue[1]"] = properties['cmis:objectTypeId']
        else:
            data["propertyValue[1]"] = "cmis:folder"

        prop_count = 2
        for prop in properties:
            data[f"propertyId[{prop_count}]"] = prop.key
            data[f"propertyValue[{prop_count}]"] = prop
            prop_count += 1

        json_response = self.post_request(self.root_folder_url, data=data)
        return Folder(json_response)

    def create_document(self, name, properties, content_file=None, **kwargs):
        data = {
            "objectId": self.objectId,
            "cmisaction": "createDocument",
            "propertyId[0]": "cmis:name",
            "propertyValue[0]": name
        }

        data["propertyId[1]"] = "cmis:objectTypeId"
        if 'cmis:objectTypeId' in properties.keys():
            data["propertyValue[1]"] = properties['cmis:objectTypeId']
        else:
            data["propertyValue[1]"] = "drc:document"

        prop_count = 2
        for prop_key, prop_value in properties.items():
            if isinstance(prop_value, date):
                prop_value = prop_value.strftime('%Y-%m-%dT%H:%I:%S.000Z')

            data[f"propertyId[{prop_count}]"] = prop_key
            data[f"propertyValue[{prop_count}]"] = prop_value
            prop_count += 1

        mimetype = None
        # need to determine the mime type
        if not mimetype and hasattr(content_file, 'name'):
            mimetype, _encoding = mimetypes.guess_type(content_file.name)

        if not mimetype:
            mimetype = 'application/binary'

        files = {name: (name, content_file, mimetype)}

        json_response = self.post_request(self.root_folder_url, data=data, files=files)
        return Document(json_response)
