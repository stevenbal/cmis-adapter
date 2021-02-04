from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.utils.translation import ugettext_lazy as _
from django.views import View

from solo.admin import SingletonModelAdmin

from .forms import CMISConfigAdminForm, UrlMappingInlineFormSet
from .models import CMISConfig, UrlMapping


class CMISConnectionJSONView(View):
    """Retrieve the vendor of the DMS behind the CMIS-connection."""

    model_admin = None

    def _get_status(self):
        """Retrieve the vendor from the CMIS repository."""
        cmis_config = CMISConfig.get_solo()
        if not cmis_config or not cmis_config.client_url:
            return _("N/A")

        try:
            from .client_builder import get_cmis_client

            return _("OK ({})").format(get_cmis_client().vendor)
        except KeyError:
            return _("Error: Unable to retrieve vendor)")
        except Exception as e:
            return _("Error: {}").format(e)

    def get(self, request, *args, **kwargs):
        """Return a JSON response showing the vendor or an error message."""
        if not self.has_perm(request):
            return JsonResponse({"error": "403 Forbidden"}, status=403)

        return JsonResponse({"status": self._get_status()})

    def has_perm(self, request, obj=None):
        """Check if user has permission to access the related model."""
        return self.model_admin.has_view_permission(request, obj=obj)


class UrlMappingAdmin(admin.TabularInline):
    model = UrlMapping
    formset = UrlMappingInlineFormSet
    can_delete = False
    extra = 1

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(CMISConfig)
class CMISConfigAdmin(SingletonModelAdmin):
    inlines = [UrlMappingAdmin]
    change_form_template = "configuration_form.html"
    form = CMISConfigAdminForm

    readonly_fields = [
        "cmis_connection",
        "cmis_url_mapping_enabled",
    ]
    fieldsets = [
        (
            _("General"),
            {"fields": ("cmis_connection",)},
        ),
        (
            _("DMS Credentials"),
            {
                "fields": (
                    "client_user",
                    "client_password",
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
                    "main_repo_id",
                    "zaak_folder_path",
                    "other_folder_path",
                    "cmis_url_mapping_enabled",
                )
            },
        ),
    ]

    class Media:
        js = ("drc_cmis/js/cmis_config.js",)

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path(
                "api/connection",
                self.admin_site.admin_view(self.cmis_connection_view),
                name="cmisconfig_api_connection",
            )
        ]
        return extra_urls + urls

    def cmis_connection_view(self, request):
        return CMISConnectionJSONView.as_view(model_admin=self)(request)

    def cmis_connection(self, obj=None):
        return "..."

    def cmis_url_mapping_enabled(self, obj=None):
        return settings.CMIS_URL_MAPPING_ENABLED

    cmis_connection.short_description = _("CMIS connection")

    cmis_url_mapping_enabled.short_description = _("URL Mapping enabled")
    cmis_url_mapping_enabled.boolean = True
