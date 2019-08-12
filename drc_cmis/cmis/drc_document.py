from drc_cmis.client.mapper import DOCUMENT_MAP


class Document:
    def __init__(self, data):
        self.data = data
        self.properties = dict(data.get('properties'))

    def __getattr__(self, name):
        return self.properties.get(DOCUMENT_MAP.get(name), {}).get('value')
