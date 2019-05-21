import sys

from django.conf import settings


class _Settings(object):

    @property
    def ENKELVOUDIGINFORMATIEOBJECT_MODEL(self):
        return getattr(settings, "ENKELVOUDIGINFORMATIEOBJECT_MODEL", "datamodel.EnkelvoudigInformatieObject")

    def __getattr__(self, name):
        return globals()[name]


# other parts of itun that you WANT to code in
# module-ish ways
sys.modules[__name__] = _Settings()
