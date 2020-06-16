from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import CMISConfig


@admin.register(CMISConfig)
class CMISConfigAdmin(SingletonModelAdmin):
    pass
