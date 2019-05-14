from django.db import models

from solo.models import SingletonModel

from drc_cmis import settings

from .choices import ChangeLogStatus
from .utils import get_model_value


class ChangeLog(models.Model):
    token = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True, unique=True)
    status = models.CharField(max_length=20, choices=ChangeLogStatus.choices, default=ChangeLogStatus.in_progress)

    class Meta:
        verbose_name = "Changelog"
        verbose_name_plural = "Changelogs"
        ordering = ("created_on",)


class DRCCMISConnection(models.Model):
    cmis_object_id = models.TextField(help_text="CMIS storage object id, internal use only", blank=True)
    enkelvoudiginformatieobject = models.OneToOneField(
        settings.ENKELVOUDIGINFORMATIEOBJECT_MODEL, on_delete=models.CASCADE,
        related_name='cmisstorage'
    )

    CMIS_MAPPING = {
        "zsdms:documenttaal": "taal",
        "zsdms:documentLink": "link",
        "cmis:name": "titel",
        "zsdms:documentIdentificatie": "identificatie",
        "zsdms:documentcreatiedatum": "creatiedatum",
        "zsdms:documentontvangstdatum": "ontvangstdatum",
        "zsdms:documentbeschrijving": "beschrijving",
        "zsdms:documentverzenddatum": "verzenddatum",
        "zsdms:vertrouwelijkaanduiding": "vertrouwelijkheidaanduiding",
        "zsdms:documentauteur": "auteur",
        "zsdms:documentstatus": "status",
        "zsdms:dct.omschrijving": "informatieobjecttype",
    }

    def __str__(self):
        return f"CMIS koppeling voor {self.enkelvoudiginformatieobject}"

    def set_cmis_doc(self, cmis_doc):
        self.cmis_object_id = cmis_doc.getObjectId().rsplit(";")[0]
        self.save()

    def get_cmis_properties(self, allow_none=True):
        """
        Returns the CMIS properties as dict.

        :param allow_none: Converts `None` to  empty string if `False` (default).
        :return: The `dict` of CMIS properties.
        """
        result = {}
        for cmis_property, field_name in self.CMIS_MAPPING.items():
            val = get_model_value(self.enkelvoudiginformatieobject, field_name)
            if val is None:
                if not allow_none:
                    val = ""
            result[cmis_property] = val

        return result

    cmis_properties = property(get_cmis_properties)

    def update_cmis_properties(self, new_cmis_properties, commit=False):
        if not self.pk:
            raise ValueError("Cannot update CMIS properties on unsaved instance.")

        updated_objects = set()

        for cmis_property, _field_name in self.CMIS_MAPPING.items():
            if cmis_property not in new_cmis_properties:
                continue
            updated_objects.add(self)

        if commit:
            for obj in updated_objects:
                obj.save()

        return updated_objects


class CMISConfiguration(SingletonModel):
    client_url = models.URLField(default='http://localhost:8082/alfresco/cmisatom')
    client_user = models.CharField(max_length=200, default='admin')
    client_password = models.CharField(max_length=200, default='admin')
    sender_property = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return u"CMIS Configuration"

    class Meta:
        verbose_name = "CMIS Configuration"
