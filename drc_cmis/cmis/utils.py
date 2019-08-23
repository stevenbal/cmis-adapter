import requests

from drc_cmis.client.exceptions import GetFirstException


class CMISRequest:
    def setup(self):
        from drc_cmis.models import CMISConfig
        config = CMISConfig.get_solo()

        self.url = config.client_url
        self.root_url = f"{self.url}/root"
        self.user = config.client_user
        self.password = config.client_password
        # assert False, self.root_url

    def _get(self, url, params=None):
        self.setup()

        response = requests.get(url, params=params, auth=(self.user, self.password))
        if not response.ok:
            raise Exception('Error with the query')

        if response.headers.get('Content-Type').startswith('application/json'):
            return response.json()
        return response.text

    def _request(self, data, url=None, files=None):
        self.setup()
        if not url:
            url = self.url

        print(url, data)
        response = requests.post(url, data=data, auth=(self.user, self.password), files=files)
        if not response.ok:
            error = response.json()
            raise Exception(error.get('message'))
        return response.json()

    def _get_first(self, json, return_type):
        if len(json['results']) == 0:
            raise GetFirstException()
            # error_string = "Document met identificatie {} bestaat niet in het CMIS connection".format(identification)
            # raise DocumentDoesNotExistError(error_string)

        return return_type(json['results'][0])

    def _get_all(self, json, return_type):
        results = []
        for item in json['results']:
            results.append(return_type(item))
        return results
