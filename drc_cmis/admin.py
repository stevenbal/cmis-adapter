from django.contrib import admin

# from drc.plugins.models import StorageConfig
from solo.admin import SingletonModelAdmin

from .models import CMISConfiguration, DRCCMISConnection


class DRCCMISConnectionAdmin(admin.ModelAdmin):
    list_display = ('enkelvoudiginformatieobject', )
    search_fields = ('enkelvoudiginformatieobject', )


# config = StorageConfig.get_solo()
# if config.cmis_storage:
admin.site.register(DRCCMISConnection, DRCCMISConnectionAdmin)
admin.site.register(CMISConfiguration, SingletonModelAdmin)
