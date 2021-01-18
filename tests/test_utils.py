import os
import re
import uuid
from unittest import skipIf

from django.test import TestCase

from drc_cmis.webservice.drc_document import Document
from drc_cmis.webservice.utils import extract_content, make_soap_envelope

from .mixins import DMSMixin


class WebserviceUtilsTests(TestCase):
    def test_extract_content_from_corsa_response(self):
        corsa_response = b'--uuid:8e14725d-a58b-4532-98be-27ed9226f17f\r\nContent-Type: application/xop+xml; charset=UTF-8; type="text/xml"\r\nContent-Transfer-Encoding: binary\r\nContent-ID: <root.message@cxf.apache.org>\r\n\r\n<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Header xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" soap:mustUnderstand="1"><wsu:Timestamp wsu:Id="TS-d88631cd-fdef-45c0-8e70-2f34873df125"><wsu:Created>2020-12-03T12:32:28.515Z</wsu:Created><wsu:Expires>2020-12-03T12:37:28.515Z</wsu:Expires></wsu:Timestamp></wsse:Security></SOAP-ENV:Header><soap:Body><getContentStreamResponse xmlns="http://docs.oasis-open.org/ns/cmis/messaging/200908/" xmlns:ns2="http://docs.oasis-open.org/ns/cmis/core/200908/"><contentStream><length>17</length><mimeType>application/octet-stream</mimeType><filename>filename</filename><stream><xop:Include xmlns:xop="http://www.w3.org/2004/08/xop/include" href="cid:7878fd49-6f1d-4d2f-9a38-54df57d1c08a-11@http%3A%2F%2Fdocs.oasis-open.org%2Fns%2Fcmis%2Fmessaging%2F200908%2F"/></stream></contentStream></getContentStreamResponse></soap:Body></soap:Envelope>\r\n--uuid:8e14725d-a58b-4532-98be-27ed9226f17f\r\nContent-Type: application/octet-stream\r\nContent-Transfer-Encoding: binary\r\nContent-ID: <7878fd49-6f1d-4d2f-9a38-54df57d1c08a-11@http://docs.oasis-open.org/ns/cmis/messaging/200908/>\r\nContent-Disposition: attachment;name="1c41733e-aae9-45ac-840c-2cd5aa00c2a8.TMP366060064106742183.tmp"\r\n\r\nsome file content\r\n--uuid:8e14725d-a58b-4532-98be-27ed9226f17f--'
        content_stream = extract_content(corsa_response)
        content = content_stream.read()

        self.assertEqual(content, b"some file content")

    def test_extract_content_from_alfresco_response(self):
        alfresco_response = b'\r\n--uuid:b4e1dca5-7b02-4697-a602-8650e3e41ce4\r\nContent-Type: application/xop+xml; charset=UTF-8; type="text/xml"\r\nContent-Transfer-Encoding: binary\r\nContent-ID: <root.message@cxf.apache.org>\r\n\r\n<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><getContentStreamResponse xmlns="http://docs.oasis-open.org/ns/cmis/messaging/200908/" xmlns:ns2="http://docs.oasis-open.org/ns/cmis/core/200908/"><contentStream><length>17</length><mimeType>text/plain</mimeType><filename>detailed summary-KJJY4M (Working Copy)</filename><stream><xop:Include xmlns:xop="http://www.w3.org/2004/08/xop/include" href="cid:1009d1c8-3689-469f-816b-f06d595aedd8-1@docs.oasis-open.org"/></stream></contentStream></getContentStreamResponse></soap:Body></soap:Envelope>\r\n--uuid:b4e1dca5-7b02-4697-a602-8650e3e41ce4\r\nContent-Type: text/plain\r\nContent-Transfer-Encoding: binary\r\nContent-ID: <1009d1c8-3689-469f-816b-f06d595aedd8-1@docs.oasis-open.org>\r\nContent-Disposition: attachment;name="detailed summary-KJJY4M (Working Copy)"\r\n\r\nsome file content\r\n--uuid:b4e1dca5-7b02-4697-a602-8650e3e41ce4--'
        content_stream = extract_content(alfresco_response)
        content = content_stream.read()

        self.assertEqual(content, b"some file content")


@skipIf(
    os.getenv("CMIS_BINDING") != "WEBSERVICE",
    "The properties are built differently with different bindings",
)
class WebserviceContentTests(DMSMixin, TestCase):
    def test_create_document_with_filename(self):
        properties = {
            "bronorganisatie": "159351741",
            "integriteitwaarde": "Something",
            "verwijderd": "false",
            "ontvangstdatum": "2020-07-28",
            "versie": "1.0",
            "creatiedatum": "2018-06-27",
            "titel": "detailed summary",
            "bestandsnaam": "filename.txt",
        }

        cmis_properties = Document.build_properties(data=properties)
        other_folder = self.cmis_client.get_or_create_other_folder()

        soap_envelope = make_soap_envelope(
            auth=(self.cmis_client.user, self.cmis_client.password),
            repository_id=self.cmis_client.main_repo_id,
            folder_id=other_folder.objectId,
            properties=cmis_properties,
            cmis_action="createDocument",
            content_id=str(uuid.uuid4()),
            content_filename="filename.txt",
        )

        self.assertIn("<ns:filename>filename.txt</ns:filename>", soap_envelope.toxml())
        self.assertIn("<ns:mimeType>text/plain</ns:mimeType>", soap_envelope.toxml())

    def test_create_document_without_filename(self):
        # No bestandsnaam
        properties = {
            "bronorganisatie": "159351741",
            "integriteitwaarde": "Something",
            "verwijderd": "false",
            "ontvangstdatum": "2020-07-28",
            "versie": "1.0",
            "creatiedatum": "2018-06-27",
            "titel": "detailed summary",
        }

        cmis_properties = Document.build_properties(data=properties)
        other_folder = self.cmis_client.get_or_create_other_folder()

        soap_envelope = make_soap_envelope(
            auth=(self.cmis_client.user, self.cmis_client.password),
            repository_id=self.cmis_client.main_repo_id,
            folder_id=other_folder.objectId,
            properties=cmis_properties,
            cmis_action="createDocument",
            content_id=str(uuid.uuid4()),  # No content_filename
        )

        # If the pattern is not found, raises an exception.
        # The default filename is a random string of len 6 with characters A-Z and 0-9
        re.search(
            r"<ns:filename>[0-9A-Z]{6}<\/ns:filename>", soap_envelope.toxml()
        ).group(0)
        self.assertIn(
            "<ns:mimeType>application/octet-stream</ns:mimeType>", soap_envelope.toxml()
        )
