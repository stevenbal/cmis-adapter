import logging
from typing import BinaryIO, List, Optional, Tuple, Union

import requests

from drc_cmis.utils.exceptions import (
    CmisBaseException,
    CmisInvalidArgumentException,
    CmisNotSupportedException,
    CmisObjectNotFoundException,
    CmisPermissionDeniedException,
    CmisRepositoryDoesNotExist,
    CmisRuntimeException,
    CmisUpdateConflictException,
)
from drc_cmis.webservice.utils import (
    extract_repository_ids_from_xml,
    extract_root_folder_id_from_xml,
    extract_xml_from_soap,
    make_soap_envelope,
    pretty_xml,
)

logger = logging.getLogger(__name__)


class SOAPCMISRequest:
    _boundary = "------=_Part_52_1132425564.1594208078802"

    _headers = {
        "Content-Type": 'multipart/related; type="application/xop+xml"; start="<rootpart@soapui.org>"; '
        'start-info="application/soap+xml"; boundary="----=_Part_52_1132425564.1594208078802"',
        "SOAPAction": "",
        "MIME-Version": "1.0",
    }

    _envelope_headers = {
        "Content-Type": 'application/xop+xml; charset=UTF-8; type="application/soap+xml"',
        "Content-Transfer-Encoding": "8bit",
        "Content-ID": "<rootpart@soapui.org>",
    }

    _main_repo_id = None

    @property
    def config(self):
        """
        Lazily load the config so that no DB queries are done while Django is starting.
        """
        from drc_cmis.models import CMISConfig

        return CMISConfig.get_solo()

    @property
    def user(self):
        return self.config.client_user

    @property
    def password(self):
        return self.config.client_password

    @property
    def base_url(self):
        """Return the base URL

        For example, for Alfresco running locally the base URL for SOAP requests is
        http://localhost:8082/alfresco/cmisws
        """
        return self.config.client_url

    @property
    def main_repo_id(self) -> str:
        """Get ID of the CMS main repository"""

        if self._main_repo_id is None:
            configured_main_repo_id = self.config.main_repo_id

            # Retrieving the IDs of all repositories in the CMS
            soap_envelope = make_soap_envelope(
                auth=(self.user, self.password), cmis_action="getRepositories"
            )

            logger.debug(soap_envelope.toprettyxml())

            soap_response = self.request(
                "RepositoryService", soap_envelope=soap_envelope.toxml()
            )

            xml_response = extract_xml_from_soap(soap_response)
            logger.debug(pretty_xml(xml_response))

            all_repositories_ids = extract_repository_ids_from_xml(xml_response)

            # If no main repository ID is configured, take the ID of the first repository returned.
            if configured_main_repo_id == "":
                self._main_repo_id = all_repositories_ids[0]
            else:
                if configured_main_repo_id not in all_repositories_ids:
                    raise CmisRepositoryDoesNotExist(
                        "The configured repository ID does not exist."
                    )

                self._main_repo_id = configured_main_repo_id

        return self._main_repo_id

    @property
    def root_folder_id(self) -> str:
        """Get the ID of the folder where all folders/documents will be created"""

        if self._root_folder_id is None:
            soap_envelope = make_soap_envelope(
                auth=(self.user, self.password),
                cmis_action="getRepositoryInfo",
                repository_id=self.main_repo_id,
            )
            logger.debug(soap_envelope.toprettyxml())
            soap_response = self.request(
                "RepositoryService", soap_envelope=soap_envelope.toxml()
            )

            xml_response = extract_xml_from_soap(soap_response)
            logger.debug(pretty_xml(xml_response))
            self._root_folder_id = extract_root_folder_id_from_xml(xml_response)

        return self._root_folder_id

    def request(
        self,
        path: str,
        soap_envelope: str,
        attachments: Optional[List[Tuple[str, BinaryIO]]] = None,
        keep_binary: bool = False,
    ) -> Union[str, bytes]:
        """Make request with MTOM attachment.

        :param path: string, path where to post the request
        :param soap_envelope: string, XML which can contain zero or more references to attachments
        (in the form of `cid:<contentId>`)
        :param attachments: list of tuples, each tuple contains the content ID used in the XML (string) and the I/O
        stream for the attachment.
        :param keep_binary: whether to keep the body of the response as binary or convert it to a string.
        :return: string or bytes, the content of the response
        """
        url = f"{self.base_url}/{path.lstrip('/')}"

        envelope_header = ""
        for key, value in self._envelope_headers.items():
            envelope_header += f"{key}: {value}\n"

        # Format the body of the request
        body = f"\n{self._boundary}\n{envelope_header}\n{soap_envelope}\n\n".encode(
            "utf-8"
        )

        # Adding the attachments
        if attachments is not None:
            for attachment in attachments:
                content_id, content_stream = attachment
                file_attachment_headers = {
                    "Content-Type": "application/octet-stream",
                    "Content-Transfer-Encoding": "binary",
                    "Content-ID": f"<{content_id}>",
                }

                xml_attachment_header = ""
                for key, value in file_attachment_headers.items():
                    xml_attachment_header += f"{key}: {value}\n"

                content_stream.seek(0)
                body += f"{self._boundary}\n{xml_attachment_header}\n".encode("utf-8")
                body += content_stream.read()  # Reads binary

        body += f"{self._boundary}--\n".encode("utf-8")
        soap_response = requests.post(url, data=body, headers=self._headers, files=[])
        if not soap_response.ok:
            error = soap_response.text
            if soap_response.status_code == 401:
                raise CmisPermissionDeniedException(
                    status=soap_response.status_code,
                    url=url,
                    message=error,
                    code=401,
                )
            elif soap_response.status_code == 400:
                raise CmisInvalidArgumentException(
                    status=soap_response.status_code,
                    url=url,
                    message=error,
                    code=400,
                )
            elif soap_response.status_code == 404:
                raise CmisObjectNotFoundException(
                    status=soap_response.status_code,
                    url=url,
                    message=error,
                    code=404,
                )
            elif soap_response.status_code == 403:
                raise CmisPermissionDeniedException(
                    status=soap_response.status_code,
                    url=url,
                    message=error,
                    code=403,
                )
            elif soap_response.status_code == 405:
                raise CmisNotSupportedException(
                    status=soap_response.status_code,
                    url=url,
                    message=error,
                    code=405,
                )
            elif soap_response.status_code == 409:
                raise CmisUpdateConflictException(
                    status=soap_response.status_code,
                    url=url,
                    message=error,
                    code=409,
                )
            elif soap_response.status_code == 500:
                raise CmisRuntimeException(
                    status=soap_response.status_code,
                    url=url,
                    message=error,
                    code=500,
                )
            else:
                raise CmisBaseException(
                    status=soap_response.status_code,
                    url=url,
                    message=error,
                    code=soap_response.status_code,
                )

        if keep_binary:
            return soap_response.content
        return soap_response.content.decode("utf-8")
