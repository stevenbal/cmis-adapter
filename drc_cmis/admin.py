from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import CMISConfiguration, DRCCMISConnection


@admin.register(DRCCMISConnection)
class DRCCMISConnectionAdmin(admin.ModelAdmin):
    list_display = ('enkelvoudiginformatieobject', )
    search_fields = ('enkelvoudiginformatieobject', )


admin.site.register(CMISConfiguration, SingletonModelAdmin)
