import requests


class GetFirstException(Exception):
    pass


class CMISRequest:
    def setup(self):
        from drc_cmis.models import CMISConfig
        config = CMISConfig.get_solo()

        self.url = config.client_url
        self.user = config.client_user
        self.password = config.client_password

    def _request(self, data):
        self.setup()
        print(self.url, data)
        response = requests.post(self.url, data=data, auth=(self.user, self.password))
        if not response.ok:
            print(response.json())
            raise Exception('Error with the query')
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
