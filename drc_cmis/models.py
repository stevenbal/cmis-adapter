import re

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _

import pytz
from djchoices import ChoiceItem, DjangoChoices
from solo.models import SingletonModel

from .utils.exceptions import NoOtherBaseFolderException, NoZaakBaseFolderException
from .utils.folder import get_folder_structure
from .validators import other_folder_path_validator, zaak_folder_path_validator


class CMISConfig(SingletonModel):
    BINDING_CHOICES = [
        ("BROWSER", "Browser binding (CMIS 1.1)"),
        ("WEBSERVICE", "Web service binding (CMIS 1.0)"),
    ]

    client_url = models.URLField(
        default="http://localhost:8082/alfresco/api/-default-/public/cmis/versions/1.1/browser",
        help_text="API URL for DMS. For example, for alfresco this can be "
        "http://domain_name:port_number/alfresco/api/-default-/public/cmis/versions/1.1/browser",
    )
    binding = models.CharField(
        choices=BINDING_CHOICES,
        default="BROWSER",
        max_length=200,
    )
    time_zone = models.CharField(
        default="UTC",
        choices=[(k, k) for k in pytz.common_timezones],
        max_length=200,
        help_text="The time zone of the DMS. Only needed when using Browser binding.",
    )
    client_user = models.CharField(
        max_length=200, default="admin", help_text="Username for logging into DMS"
    )
    client_password = models.CharField(
        max_length=200, default="admin", help_text="Password for logging into DMS"
    )
    zaak_folder_path = models.CharField(
        max_length=500,
        default="/DRC/{{ zaaktype }}/{{ year }}/{{ month }}/{{ day }}/{{ zaak }}/",
        validators=[zaak_folder_path_validator],
        help_text=_("The path where documents related to zaken are saved."),
    )
    other_folder_path = models.CharField(
        max_length=500,
        default="/DRC/{{ year }}/{{ month }}/{{ day }}/",
        validators=[other_folder_path_validator],
        help_text=_("The path where other documents are saved."),
    )

    def __str__(self):
        return "CMIS Configuration"

    class Meta:
        verbose_name = "CMIS Configuration"

    def get_zaak_base_folder_name(self) -> str:
        folders = get_folder_structure(self.zaak_folder_path)
        if len(folders) > 0:
            folder_name = re.search(r"^{{ (.+?) }}$", folders[0].folder_name)
            if folder_name is not None:
                raise NoZaakBaseFolderException("No zaak base folder in use.")
            return folders[0].folder_name
        raise ImproperlyConfigured("The 'zaak_folder_path' must be configured.")

    def get_other_base_folder_name(self) -> str:
        folders = get_folder_structure(self.other_folder_path)
        if len(folders) > 0:
            folder_name = re.search(r"^{{ (.+?) }}$", folders[0].folder_name)
            if folder_name is not None:
                raise NoOtherBaseFolderException("No other base folder in use.")
            return folders[0].folder_name
        raise ImproperlyConfigured("The 'other_folder_path' must be configured.")


class Vendor(DjangoChoices):
    alfresco = ChoiceItem()
    bct = ChoiceItem()
