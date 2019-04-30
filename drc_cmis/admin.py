from django.contrib import admin

from .models import DRCCMISConnection


@admin.register(DRCCMISConnection)
class DRCCMISConnectionAdmin(admin.ModelAdmin):
    pass
