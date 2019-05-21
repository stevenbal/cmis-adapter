from django.db import models

from solo.models import SingletonModel


class CMISConfig(SingletonModel):
    client_url = models.URLField(default='http://localhost:8082/alfresco/cmisatom')
    client_user = models.CharField(max_length=200, default='admin')
    client_password = models.CharField(max_length=200, default='admin')

    def __unicode__(self):
        return "CMIS Configuration"

    class Meta:
        verbose_name = "CMIS Configuration"
