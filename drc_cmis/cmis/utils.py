import requests

from drc_cmis.client.exceptions import GetFirstException


class CMISRequest:
    def __init__(self):
        from drc_cmis.models import CMISConfig
        config = CMISConfig.get_solo()

        self.base_url = config.client_url
        self.root_folder_url = f"{self.base_url}/root"
        self.user = config.client_user
        self.password = config.client_password

    def get_request(self, url, params=None):
        print('= GET_REQUEST ==================================================')
        print(url, params)
        print('= END GET_REQUEST ==================================================')
        response = requests.get(url, params=params, auth=(self.user, self.password))
        if not response.ok:
            raise Exception('Error with the query')

        if response.headers.get('Content-Type').startswith('application/json'):
            return response.json()
        return response.text

    def post_request(self, url, data, files=None):
        print('= POST_REQUEST ==================================================')
        print(url, data)
        print('= END POST_REQUEST ==================================================')
        response = requests.post(url, data=data, auth=(self.user, self.password), files=files)
        if not response.ok:
            error = response.json()
            raise Exception(error.get('message'))
        return response.json()

    def get_first_result(self, json, return_type):
        if len(json.get('results')) == 0:
            raise GetFirstException()

        return return_type(json.get('results')[0])

    def get_all_resutls(self, json, return_type):
        results = []
        for item in json.get('results'):
            results.append(return_type(item))
        return results

    def get_all_objects(self, json, return_type):
        objects = []
        for item in json:
            objects.append(return_type(item.get('object')))
        return objects
