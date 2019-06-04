"""
Listen to the notifications that are send by the NRC
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
import requests
from vng_api_common.models import APICredential
from urllib.parse import urlsplit
from zds_client.client import Client
from drc_cmis.client import cmis_client

class ZakenNotificationView(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    # authentication_classes = (BaseAuthRequired, )

    def post(self, request, format=None):
        """
        {
            "kanaal": "zaken",
            "hoofdObject": "https://ref.tst.vng.cloud/zrc/api/v1/zaken/ddc6d192",
            "resource": "status",
            "resourceUrl": "https://ref.tst.vng.cloud/zrc/api/v1/statussen/44fdcebf",
            "actie": "create",
            "aanmaakdatum": "2019-03-27T10:59:13Z",
            "kenmerken": {
                "bronorganisatie": "224557609",
                "zaaktype": "https://ref.tst.vng.cloud/ztc/api/v1/catalogussen/39732928/zaaktypen/53c5c164",
                "vertrouwelijkheidaanduiding": "openbaar"
            }
        }
        """
        data = request.data

        if data.get('actie') == 'create' and data.get('resource') == 'zaak':
            zaaktype_url = data.get('kenmerken', {}).get('zaaktype')
            auth = APICredential.get_auth(zaaktype_url)
            client = Client.from_url(zaaktype_url)
            client.auth = auth
            zaaktype_data = client.retrieve('zaaktype', url=zaaktype_url)
            zaaktype_folder = cmis_client.get_or_create_zaaktype_folder(zaaktype_data)

            zaak_url = data.get('resource_url')
            auth = APICredential.get_auth(zaak_url)
            client = Client.from_url(zaak_url)
            client.auth = auth
            zaak_data = client.retrieve('zaak', url=zaak_url)
            zaak_folder = cmis_client.get_or_create_zaak_folder(zaak_data, zaaktype_folder)
            return Response('Ok')
        return Response('Ok, not acted on the request.')
