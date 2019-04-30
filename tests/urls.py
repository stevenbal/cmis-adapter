from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cmis/', include(('drc_cmis.urls', 'drc_cmis'), namespace='cmis')),
]
