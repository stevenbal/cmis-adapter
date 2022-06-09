import io
import os
from unittest import skipIf
from unittest.mock import patch

from django.test import TestCase

from drc_cmis.models import CMISConfig, UrlMapping

from .mixins import DMSMixin


class DeleteOIORelationTests(DMSMixin, TestCase):
    base_zaak_url = "https://openzaak.utrechtproeftuin.nl/zaken/api/v1/"
    base_zaaktype_url = "https://openzaak.utrechtproeftuin.nl/catalogi/api/v1/"
    base_besluit_url = "https://openzaak.utrechtproeftuin.nl/besluiten/api/v1/"

    zaaktype = {
        "url": f"{base_zaaktype_url}zaaktypen/0119dd4e-7be9-477e-bccf-75023b1453c1",
        "identificatie": 1,
        "omschrijving": "Melding Openbare Ruimte",
    }

    zaak1 = {
        "url": f"{base_zaak_url}zaken/1c8e36be-338c-4c07-ac5e-1adf55bec04a",
        "identificatie": "1bcfd0d6-c817-428c-a3f4-4047038c184d",
        "zaaktype": zaaktype["url"],
        "startdatum": "2023-12-06",
        "einddatum": None,
        "registratiedatum": "2019-04-17",
        "bronorganisatie": "509381406",
    }
    zaak2 = {
        "url": f"{base_zaak_url}zaken/305e7c70-8a11-4321-80cc-e60498090fab",
        "identificatie": "1717b1f0-16e5-42d4-ba28-cbce211bb94b",
        "zaaktype": zaaktype["url"],
        "startdatum": "2023-12-06",
        "einddatum": None,
        "registratiedatum": "2019-04-17",
        "bronorganisatie": "509381406",
    }
    besluit = {
        "url": f"{base_besluit_url}besluit/9d3dd93a-778d-4d26-8c48-db7b2a584307",
        "verantwoordelijke_organisatie": "517439943",
        "identificatie": "123123",
        "besluittype": "https://openzaak.utrechtproeftuin.nl/catalogi/api/v1/besluittype/ba0a30d4-5b4d-464c-b5d3-855ad796492f",
        "zaak": zaak1["url"],
        "datum": "2018-09-06",
        "toelichting": "Vergunning verleend.",
        "ingangsdatum": "2018-10-01",
        "vervaldatum": "2018-11-01",
    }
    document = {
        "bronorganisatie": "159351741",
        "creatiedatum": "2011-09-01T13:20:30+03:00",
        "titel": "detailed summary",
        "auteur": "test_auteur",
        "formaat": "txt",
        "taal": "eng",
        "bestandsnaam": "dummy.txt",
        "link": "https://drc.utrechtproeftuin.nl/api/v1/enkelvoudiginformatieobjecten/d06f86e0-1c3a-49cf-b5cd-01c079cf8147/download",
        "beschrijving": "test_beschrijving",
        "vertrouwelijkheidaanduiding": "openbaar",
    }

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        config = CMISConfig.get_solo()

        UrlMapping.objects.create(
            long_pattern="drc.utrechtproeftuin.nl",
            short_pattern="drc.nl",
            config=config,
        )
        UrlMapping.objects.create(
            long_pattern="openzaak.utrechtproeftuin.nl/besluiten",
            short_pattern="oz.nl/besluit",
            config=config,
        )
        UrlMapping.objects.create(
            long_pattern="openzaak.utrechtproeftuin.nl/zaken",
            short_pattern="oz.nl/zaken",
            config=config,
        )
        UrlMapping.objects.create(
            long_pattern="openzaak.utrechtproeftuin.nl/catalogi",
            short_pattern="oz.nl/catalogi",
            config=config,
        )

    def test_delete_oio_removes_document_copy_and_gebruiksrechten(self):
        # Creating the document in the default folder
        document = self.cmis_client.create_document(
            identification="9124c668-db3f-4198-8823-4c21fed430d0",
            data=self.document,
            content=io.BytesIO(b"some file content"),
            bronorganisatie="159351741",
        )

        # Create gebruiksrechten in the default folder
        gebruiksrechten_data = {
            "informatieobject": f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}",
            "startdatum": "2018-12-24T00:00:00Z",
            "omschrijving_voorwaarden": "Een hele set onredelijke voorwaarden",
        }
        self.cmis_client.create_gebruiksrechten(data=gebruiksrechten_data)

        # Creating 2 relations
        oio1 = {
            "zaak": self.zaak1["url"],
            "informatieobject": f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}",
            "object_type": "zaak",
        }
        self.cmis_client.create_oio(
            oio_data=oio1, zaak_data=self.zaak1, zaaktype_data=self.zaaktype
        )

        oio2 = {
            "zaak": self.zaak2["url"],
            "informatieobject": f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}",
            "object_type": "zaak",
        }
        oio2 = self.cmis_client.create_oio(
            oio_data=oio2, zaak_data=self.zaak2, zaaktype_data=self.zaaktype
        )
        related_data2_folder = oio2.get_parent_folders()[0]

        # When OIO2 is created, the document and its gebruiksrechten are copied to the zaak2 folder
        # so 2 documents and 2 gebruiksrechten files exist (the original and 1 copy)
        zaak2_folder = self.cmis_client.query(
            "zaak", lhs=["drc:zaak__url = '%s'"], rhs=[self.zaak2["url"]]
        )[0]
        documents_in_zaak2 = zaak2_folder.get_children_documents()

        self.assertEqual(1, len(documents_in_zaak2))
        self.assertEqual(document.uuid, documents_in_zaak2[0].kopie_van)

        # Check that 2 gebruiksrechten files exist (the original and 1 copy)
        gebruiksrechten_files = self.cmis_client.query(
            "gebruiksrechten",
            lhs=["drc:gebruiksrechten__informatieobject = '%s'"],
            rhs=[f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}"],
        )

        self.assertEqual(2, len(gebruiksrechten_files))

        # Deleting oio2 should delete the document and gebruiksrechten in the zaak2 folder (copies of the originals)
        oio2.delete_object()

        documents_in_zaak2 = zaak2_folder.get_children_documents()
        files_in_related_data_folder = related_data2_folder.get_children_documents()

        self.assertEqual(0, len(documents_in_zaak2))
        self.assertEqual(0, len(files_in_related_data_folder))

        # Check that now only 1 gebruiksrechten file exists now (the original)
        gebruiksrechten_files = self.cmis_client.query(
            "gebruiksrechten",
            lhs=["drc:gebruiksrechten__informatieobject = '%s'"],
            rhs=[f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}"],
        )

        self.assertEqual(1, len(gebruiksrechten_files))

    def test_delete_oio_moves_document_original_and_gebruiksrechten_to_default_folder(
        self,
    ):
        # Creating the document in the default folder
        document = self.cmis_client.create_document(
            identification="9124c668-db3f-4198-8823-4c21fed430d0",
            data=self.document,
            content=io.BytesIO(b"some file content"),
            bronorganisatie="159351741",
        )

        # Create gebruiksrechten in the default folder
        gebruiksrechten_data = {
            "informatieobject": f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}",
            "startdatum": "2018-12-24T00:00:00Z",
            "omschrijving_voorwaarden": "Een hele set onredelijke voorwaarden",
        }
        self.cmis_client.create_gebruiksrechten(data=gebruiksrechten_data)

        # Creating 1 relation
        oio = {
            "zaak": self.zaak1["url"],
            "informatieobject": f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}",
            "object_type": "zaak",
        }
        oio = self.cmis_client.create_oio(
            oio_data=oio, zaak_data=self.zaak1, zaaktype_data=self.zaaktype
        )
        related_data_folder = oio.get_parent_folders()[0]

        # When OIO is created, the document and the gebruiksrechten file are moved to the zaak1 folder
        zaak1_folder = self.cmis_client.query(
            "zaak", lhs=["drc:zaak__url = '%s'"], rhs=[self.zaak1["url"]]
        )[0]
        documents_in_zaak1 = zaak1_folder.get_children_documents()

        self.assertEqual(1, len(documents_in_zaak1))
        self.assertIsNone(documents_in_zaak1[0].kopie_van)

        # Check that 1 gebruiksrechten file exist (the original, no copies)
        gebruiksrechten_files = self.cmis_client.query(
            "gebruiksrechten",
            lhs=["drc:gebruiksrechten__informatieobject = '%s'"],
            rhs=[f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}"],
        )
        self.assertEqual(1, len(gebruiksrechten_files))

        # Deleting oio should move the document and the gebruiksrechten file back to the default folder
        oio.delete_object()

        documents_in_zaak1 = zaak1_folder.get_children_documents()
        files_in_related_data_folder = related_data_folder.get_children_documents()

        self.assertEqual(0, len(documents_in_zaak1))
        self.assertEqual(0, len(files_in_related_data_folder))

        document_parent_folder = document.get_parent_folders()[0]
        default_folder = self.cmis_client.get_or_create_other_folder()

        self.assertEqual(document_parent_folder.objectId, default_folder.objectId)

        # Check that now only 1 gebruiksrechten files exist (the original), and it's in the 'Related data' folder in the
        # default folder
        gebruiksrechten_files = self.cmis_client.query(
            "gebruiksrechten",
            lhs=["drc:gebruiksrechten__informatieobject = '%s'"],
            rhs=[f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}"],
        )
        default_related_data_folder = default_folder.get_child_folder("Related data")

        self.assertEqual(1, len(gebruiksrechten_files))
        self.assertEqual(
            gebruiksrechten_files[0].get_parent_folders()[0].objectId,
            default_related_data_folder.objectId,
        )

    @patch("drc_cmis.webservice.drc_document.ObjectInformatieObject._reorganise_files")
    def test_delete_bio_does_not_rearrange_files(self, m_reorganise_files):
        # Creating the document in the default folder
        document = self.cmis_client.create_document(
            identification="9124c668-db3f-4198-8823-4c21fed430d0",
            data=self.document,
            content=io.BytesIO(b"some file content"),
            bronorganisatie="159351741",
        )

        # Creating a relation to a zaak and to a besluit
        oio1 = {
            "zaak": self.zaak1["url"],
            "informatieobject": f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}",
            "object_type": "zaak",
        }
        self.cmis_client.create_oio(
            oio_data=oio1, zaak_data=self.zaak1, zaaktype_data=self.zaaktype
        )

        oio2 = {
            "object": self.besluit["url"],
            "informatieobject": f"https://drc.utrechtproeftuin.nl/api/v1/documenten/{document.uuid}",
            "object_type": "besluit",
        }
        oio2 = self.cmis_client.create_oio(
            oio_data=oio2, zaak_data=self.zaak1, zaaktype_data=self.zaaktype
        )

        # Deleting the OIO referring to a besluit should not re-arrange files
        oio2.delete_object()

        m_reorganise_files.assert_not_called()
