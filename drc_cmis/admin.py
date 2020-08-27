from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from solo.admin import SingletonModelAdmin

from .models import CMISConfig


@admin.register(CMISConfig)
class CMISConfigAdmin(SingletonModelAdmin):
    readonly_fields = [
        "cmis_enabled",
    ]
    fieldsets = (
        (
            _("General"),
            {
                "fields": (
                    "cmis_enabled",
                    "dms_vendor",
                )
            },
        ),
        (
            _("Configuration"),
            {
                "fields": (
                    "client_url",
                    "binding",
                    "time_zone",
                    "zaak_folder_path",
                    "other_folder_path",
                )
            },
        ),
        (
            _("Credentials"),
            {
                "fields": (
                    "client_user",
                    "client_password",
                )
            },
        ),
    )

    def cmis_enabled(self, obj):
        return settings.CMIS_ENABLED

    cmis_enabled.short_description = _("Enabled")
    cmis_enabled.boolean = True

    def dms_vendor(self, obj):
        if not self.cmis_enabled:
            return ""

        if not obj or not obj.client_url:
            return _("(CMIS configuration incomplete)")

        try:
            from client_builder import get_cmis_client

            return get_cmis_client().vendor
        except KeyError:
            return _("(Unknown)")
        except Exception:
            return _("(Connection error)")

    dms_vendor.short_description = _("DMS Vendor")

    def has_change_permission(self, *args, **kwargs):
        return settings.CMIS_ENABLED
