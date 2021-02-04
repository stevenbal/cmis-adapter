from urllib.parse import urlparse

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

from .models import CMISConfig


class UrlMappingInlineFormSet(BaseInlineFormSet):
    def clean(self):
        for form in self.forms:
            if (
                form.is_valid()
                and form.cleaned_data.get("long_pattern")
                and form.cleaned_data.get("short_pattern")
            ):
                parsed_long_url = urlparse(form.cleaned_data["long_pattern"])
                parsed_short_url = urlparse(form.cleaned_data["short_pattern"])

                if parsed_long_url.scheme != parsed_short_url.scheme:
                    raise ValidationError(
                        _(
                            "Use the same scheme (e.g. http or https) for both the long and short pattern."
                        )
                    )


class CMISConfigAdminForm(forms.ModelForm):
    class Meta:
        model = CMISConfig
        fields = "__all__"

    # This method is used from the custom template to decide whether to render the URL mapping formset
    def cmis_url_mapping_enabled(self):
        return settings.CMIS_URL_MAPPING_ENABLED
