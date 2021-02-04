import os
from unittest import skipIf

from django.test import TestCase

from drc_cmis.models import CMISConfig, UrlMapping
from drc_cmis.webservice.utils import (
    NoURLMappingException,
    expand_url,
    extract_content,
    extract_repository_ids_from_xml,
    shrink_url,
)


@skipIf(
    os.getenv("CMIS_BINDING") != "WEBSERVICE",
    "Webservice binding specific functions",
)
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

    def test_extract_repositories_ids_alfresco(self):
        alfreso_soap_envelope = '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><getRepositoriesResponse xmlns="http://docs.oasis-open.org/ns/cmis/messaging/200908/" xmlns:ns2="http://docs.oasis-open.org/ns/cmis/core/200908/"><repositories><repositoryId>5341cc88-b2f6-4476-aff3-4add269dcb09</repositoryId><repositoryName>Main Repository</repositoryName></repositories></getRepositoriesResponse></soap:Body></soap:Envelope>'

        all_repositories_ids = extract_repository_ids_from_xml(alfreso_soap_envelope)
        self.assertEqual(len(all_repositories_ids), 1)
        self.assertEqual(
            all_repositories_ids[0], "5341cc88-b2f6-4476-aff3-4add269dcb09"
        )


@skipIf(
    os.getenv("CMIS_BINDING") != "WEBSERVICE",
    "Webservice binding specific functions",
)
class UrlMappingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        CMISConfig.objects.create(
            client_url="http://localhost:8082/alfresco/cmisws",
            binding="WEBSERVICE",
            client_user="admin",
            client_password="admin",
            zaak_folder_path="/TestZaken/{{ zaaktype }}/{{ zaak }}/",
            other_folder_path="/TestDRC/",
        )

    def test_shorten_url(self):
        config = CMISConfig.get_solo()

        UrlMapping.objects.create(
            long_pattern="https://openzaak.utrechtproeftuin.nl/zaken/",
            short_pattern="https://oz.nl/",
            config=config,
        )

        long_url = "https://openzaak.utrechtproeftuin.nl/zaken/api/v1/zaakinformatieobjecten/fc345347-3115-4f0a-8808-e392d66e1886"
        short_url = shrink_url(long_url)

        self.assertEqual(
            short_url,
            "https://oz.nl/api/v1/zaakinformatieobjecten/fc345347-3115-4f0a-8808-e392d66e1886",
        )

    def test_shorten_url_no_mapping(self):
        long_url = "https://openzaak.utrechtproeftuin.nl/zaken/api/v1/zaakinformatieobjecten/fc345347-3115-4f0a-8808-e392d66e1886"

        with self.assertRaises(NoURLMappingException):
            shrink_url(long_url)

    def test_shorten_url_multiple_mappings(self):
        long_url = "http://openzaak.utrechtproeftuin.nl/zaken/api/v1/zaakinformatieobjecten/fc345347-3115-4f0a-8808-e392d66e1886"

        config = CMISConfig.get_solo()

        UrlMapping.objects.create(
            long_pattern="http://openzaak.utrechtproeftuin.nl/zaken/",
            short_pattern="http://o.nl/zaken/",
            config=config,
        )

        UrlMapping.objects.create(
            long_pattern="http://openzaak.utrechtproeftuin.nl/",
            short_pattern="http://o.nl/",
            config=config,
        )

        short_url = shrink_url(long_url)

        self.assertEqual(
            short_url,
            "http://o.nl/zaken/api/v1/zaakinformatieobjecten/fc345347-3115-4f0a-8808-e392d66e1886",
        )

    def test_expand_url(self):
        config = CMISConfig.get_solo()

        UrlMapping.objects.create(
            long_pattern="https://openzaak.utrechtproeftuin.nl/zaken/",
            short_pattern="https://oz.nl/",
            config=config,
        )

        short_url = "https://oz.nl/api/v1/zaakinformatieobjecten/fc345347-3115-4f0a-8808-e392d66e1886"
        long_url = expand_url(short_url)

        self.assertEqual(
            long_url,
            "https://openzaak.utrechtproeftuin.nl/zaken/api/v1/zaakinformatieobjecten/fc345347-3115-4f0a-8808-e392d66e1886",
        )
