from django.contrib import admin

from .models import DRCCMISConnection


@admin.register(DRCCMISConnection)
class DRCCMISConnectionAdmin(admin.ModelAdmin):
    list_display = ('enkelvoudiginformatieobject', )
    search_fields = ('enkelvoudiginformatieobject', )
