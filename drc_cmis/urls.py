from django.conf.urls import url

from .notifications import ZakenNotificationView

urlpatterns = [
    url(r"^api/callbacks/$", ZakenNotificationView.as_view(), name="zaken-callback"),
]
