import sys

from django.conf import settings


class _Settings(object):
    @property
    def DRC_CMIS_CLIENT_URL(self):
        return getattr(settings, "DRC_CMIS_CLIENT_URL")

    @property
    def DRC_CMIS_CLIENT_USER(self):
        return getattr(settings, "DRC_CMIS_CLIENT_USER")

    @property
    def DRC_CMIS_CLIENT_USER_PASSWORD(self):
        return getattr(settings, "DRC_CMIS_CLIENT_USER_PASSWORD")

    @property
    def DRC_CMIS_SENDER_PROPERTY(self):
        return getattr(settings, "DRC_CMIS_SENDER_PROPERTY", None)

    @property
    def DRC_CMIS_UPLOAD_TO(self):
        return getattr(settings, "DRC_CMIS_UPLOAD_TO", "drc_cmis.utils.upload_to")

    @property
    def DRC_CMIS_CLIENT_CLASS(self):
        return getattr(settings, "DRC_CMIS_CLIENT_CLASS", "drc_cmis.client.CMISDRCClient")

    @property
    def DRC_CMIS_ENKELVOUDIGINFORMATIEOBJECT(self):
        return getattr(settings, "DRC_CMIS_ENKELVOUDIGINFORMATIEOBJECT", "datamodel.EnkelvoudigInformatieObject")

    @property
    def DRC_CMIS_TEMP_FOLDER_NAME(self):
        return getattr(settings, "DRC_CMIS_TEMP_FOLDER_NAME", "enkelvoudiginformatieobjecten")

    def __getattr__(self, name):
        return globals()[name]


# other parts of itun that you WANT to code in
# module-ish ways
sys.modules[__name__] = _Settings()
