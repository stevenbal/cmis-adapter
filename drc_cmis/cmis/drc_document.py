import logging
import mimetypes
from datetime import date
from io import BytesIO

from drc_cmis.client.mapper import (
    CONNECTION_MAP, DOCUMENT_MAP, REVERSE_CONNECTION_MAP, REVERSE_DOCUMENT_MAP
)

from .utils import CMISRequest

logger = logging.getLogger(__name__)


class CMISBaseObject(CMISRequest):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.properties = dict(data.get('properties', {}))

    def reload(self):
        logger.debug("CMIS: DRC_DOCUMENT: reload")
        params = {
            "objectId": self.objectId,
            "cmisselector": "object",
        }

        json_response = self.get_request(self.root_folder_url, params=params)
        self.data = json_response
        self.properties = json_response.get('properties')

    def get_object_parents(self):
        logger.debug("CMIS: DRC_DOCUMENT: get_object_parents")
        params = {
            "objectId": self.objectId,
            "cmisselector": "parents",
        }

        json_response = self.get_request(self.root_folder_url, params=params)
        return self.get_all_objects(json_response, Folder)

    def move(self, sourceFolder, targetFolder):
        data = {
            "objectId": self.objectId,
            "cmisaction": "move",
            "sourceFolderId": sourceFolder.objectId,
            "targetFolderId": targetFolder.objectId
        }
        logger.debug(f"From: {sourceFolder.name} To: {targetFolder.name}")
        logger.debug(f"From: {sourceFolder.objectTypeId} To: {targetFolder.objectTypeId}")
        # invoke the URL
        json_response = self.post_request(self.root_folder_url, data=data)
        self.data = json_response
        self.properties = json_response.get('properties')
        return self


class Document(CMISBaseObject):
    def __getattr__(self, name):
        convert_string = f"drc:{name}"
        if name in DOCUMENT_MAP:
            convert_string = DOCUMENT_MAP.get(name)
        elif name in CONNECTION_MAP:
            convert_string = CONNECTION_MAP.get(name)
        elif convert_string not in REVERSE_CONNECTION_MAP and convert_string not in REVERSE_DOCUMENT_MAP:
            convert_string = f"cmis:{name}"
        return self.properties.get(convert_string, {}).get('value')

    def checkout(self):
        logger.debug("CMIS: DRC_DOCUMENT: checkout")
        data = {"objectId": self.objectId, "cmisaction": "checkOut"}
        json_response = self.post_request(self.root_folder_url, data=data)
        return Document(json_response)

    def update_properties(self, properties):
        logger.debug("CMIS: DRC_DOCUMENT: update_properties")
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

    def get_private_working_copy(self):
        logger.debug("CMIS: DRC_DOCUMENT: get_private_working_copy")
        self.properties["cmis:objectId"]["value"] = self.properties["cmis:versionSeriesCheckedOutId"]["value"]
        return self

    def checkin(self, checkin_comment, major=True):
        logger.debug("CMIS: DRC_DOCUMENT: checkin")
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
        logger.debug("CMIS: DRC_DOCUMENT: set_content_stream")
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
        logger.debug("CMIS: DRC_DOCUMENT: get_content_stream")
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
        logger.debug("CMIS: DRC_DOCUMENT: get_children")
        data = {
            "cmisaction": "query",
            "statement": f"SELECT * FROM cmis:folder WHERE IN_FOLDER('{self.objectId}')",
        }
        json_response = self.post_request(self.base_url, data=data)
        return self.get_all_resutls(json_response, Folder)

    def create_folder(self, name, properties={}, **kwargs):
        logger.debug("CMIS: DRC_DOCUMENT: create_folder")
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
        for prop, value in properties.items():
            data[f"propertyId[{prop_count}]"] = prop
            data[f"propertyValue[{prop_count}]"] = value
            prop_count += 1

        json_response = self.post_request(self.root_folder_url, data=data)
        return Folder(json_response)

    def create_document(self, name, properties, content_file=None, **kwargs):
        logger.debug("CMIS: DRC_DOCUMENT: create_document")
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

        json_response = self.post_request(self.root_folder_url, data=data)
        cmis_doc = Document(json_response)
        return cmis_doc.set_content_stream(content_file)

    def delete_tree(self, **kwargs):
        data = {
            "objectId": self.objectId,
            "cmisaction": "deleteTree"
        }
        self.post_request(self.root_folder_url, data=data)
