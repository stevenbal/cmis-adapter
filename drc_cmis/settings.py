import sys

from django.conf import settings


class _Settings(object):
    @property
    def DRC_CMIS_UPLOAD_TO(self):
        return getattr(settings, "DRC_CMIS_UPLOAD_TO", "drc_cmis.utils.upload_to")

    @property
    def DRC_CMIS_CLIENT_CLASS(self):
        return getattr(settings, "DRC_CMIS_CLIENT_CLASS", "drc_cmis.client.CMISDRCClient")

    @property
    def ENKELVOUDIGINFORMATIEOBJECT_MODEL(self):
        return getattr(settings, "ENKELVOUDIGINFORMATIEOBJECT_MODEL", "datamodel.EnkelvoudigInformatieObject")

    @property
    def DRC_CMIS_TEMP_FOLDER_NAME(self):
        return getattr(settings, "DRC_CMIS_TEMP_FOLDER_NAME", "enkelvoudiginformatieobjecten")

    def __getattr__(self, name):
        return globals()[name]


# other parts of itun that you WANT to code in
# module-ish ways
sys.modules[__name__] = _Settings()
