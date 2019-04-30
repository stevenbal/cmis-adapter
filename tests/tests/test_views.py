from django.db.models import signals
from django.urls import reverse

import factory
from django_webtest import WebTest

from drc_cmis.client import default_client

from .factories import (
    DRCCMISConnectionFactory, EnkelvoudigInformatieObjectFactory
)
from .mixins import DMSMixin


class DownloadFileViewTests(DMSMixin, WebTest):
    @factory.django.mute_signals(signals.post_save)
    def test_download_file_404(self):
        enkelvoudig_informatie_object = EnkelvoudigInformatieObjectFactory()
        url = reverse('cmis:cmis-document-download', kwargs={'inhoud': enkelvoudig_informatie_object.uuid})
        self.app.get(url, status=404)

    def test_download_file(self):
        enkelvoudig_informatie_object = EnkelvoudigInformatieObjectFactory()
        koppeling = DRCCMISConnectionFactory(enkelvoudiginformatieobject=enkelvoudig_informatie_object)
        default_client.maak_zaakdocument_met_inhoud(koppeling, stream=enkelvoudig_informatie_object.inhoud)
        enkelvoudig_informatie_object.inhoud.seek(0)
        url = reverse('cmis:cmis-document-download', kwargs={'inhoud': enkelvoudig_informatie_object.uuid})
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, enkelvoudig_informatie_object.inhoud.read())
