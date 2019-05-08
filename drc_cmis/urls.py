from django.urls import path

from .views import DownloadFileView

app_name = 'drc_cmis'

urlpatterns = [path("content/<str:inhoud>", DownloadFileView.as_view(), name="cmis-document-download")]
