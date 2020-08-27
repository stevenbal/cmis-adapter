from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .mixins import DMSMixin


class CMISConfigAdminTests(DMSMixin, TestCase):
    def setUp(self):
        super().setUp()

        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="superuser", password="secret", email="superuser@example.com"
        )

    def test_cmis_config_page(self):
        url = reverse("admin:drc_cmis_cmisconfig_change")

        self.client.login(username=self.superuser.username, password="secret")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_cmis_connection_not_logged_in(self):
        url = reverse("admin:cmisconfig_api_connection")
        admin_login_url = reverse("admin:login")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{admin_login_url}?next={url}")

    def test_cmis_connection_no_permission(self):
        url = reverse("admin:cmisconfig_api_connection")

        self.superuser.is_superuser = False
        self.superuser.save()

        self.client.login(username=self.superuser.username, password="secret")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_cmis_connection(self):
        url = reverse("admin:cmisconfig_api_connection")

        self.client.login(username=self.superuser.username, password="secret")
        response = self.client.get(url)

        self.assertEqual(response.json(), {"status": "OK (Alfresco)"}, response.content)
