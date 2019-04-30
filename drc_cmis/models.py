from django.db import models

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
        settings.DRC_CMIS_ENKELVOUDIGINFORMATIEOBJECT, on_delete=models.CASCADE,
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
            # try:
            #     field_class = get_model_field(EnkelvoudigInformatieObject, field_name)
            # except FieldDoesNotExist:
            #     field_class = None

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
