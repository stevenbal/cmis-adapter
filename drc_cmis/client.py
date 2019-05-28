import codecs
import logging
from datetime import datetime
from io import BytesIO

from django.utils import timezone
from django.utils.text import slugify

from cmislib import CmisClient
from cmislib.exceptions import UpdateConflictException

from .choices import CMISObjectType
from .exceptions import (
    DocumentConflictException, DocumentDoesNotExistError, DocumentExistsError,
    DocumentLockedException
)
from .query import CMISQuery
from .utils import upload_to

logger = logging.getLogger(__name__)


class CMISDRCClient:
    """
    DRC client implementation using the CMIS protocol.
    """
    documents_query = CMISQuery("SELECT * FROM cmis:document as D WHERE %s")
    document_cases_query = CMISQuery("SELECT * FROM drc:document WHERE drc:oio_zaak_url IS NOT NULL")
    document_query = CMISQuery("SELECT * FROM drc:document WHERE drc:identificatie = '%s'")
    document_query = CMISQuery("SELECT * FROM cmis:document WHERE cmis:objectId = 'workspace://SpacesStore/%s;1.0'")

    _repo = None
    _root_folder = None
    _base_folder = None

    @property
    def _get_repo(self):
        """
        Connect to the CMIS repository
        """
        if not self._repo:
            from .models import CMISConfig
            config = CMISConfig.get_solo()
            _client = CmisClient(config.client_url, config.client_user, config.client_password)
            self._repo = _client.getDefaultRepository()
        return self._repo

    @property
    def _get_root_folder(self):
        if not self._root_folder:
            self._root_folder = self._get_repo.getObjectByPath("/")
        return self._root_folder

    @property
    def _get_base_folder(self):
        if not self._base_folder:
            self._base_folder = self._get_or_create_folder('DRC', self._get_root_folder)
        return self._base_folder

    def create_document(self, identificatie, data, stream=None):
        """
        :param identificatie: EnkelvoudigInformatieObject identificatie
        :param data: De data voor de properties.
        :param stream: Inhoud van het document.

        :return: AtomPubDocument instance die aangemaakt werd.
        :raises: DocumentExistsError wanneer er al een document met dezelfde identificatie bestaat, binnen de zaakfolder.
        """
        self._check_document_exists(identificatie)

        now = datetime.now()

        if stream is None:
            stream = BytesIO()

        year_folder = self._get_or_create_folder(str(now.year), self._get_base_folder)
        month_folder = self._get_or_create_folder(str(now.month), year_folder)
        day_folder = self._get_or_create_folder(str(now.day), month_folder)
        properties = self._build_properties(identificatie, data)

        return self._get_repo.createDocument(
            name=data.get('titel'), properties=properties, contentFile=stream, contentType=None,
            parentFolder=day_folder,
        )

    def get_cmis_documents(self, filter_case=False):
        """
        Gives a list of cmis documents.

        :return: :class:`AtomPubDocument` list
        """
        from .models import CMISConfig

        if filter_case:
            query = self.document_cases_query()
        else:
            config = CMISConfig.get_solo()
            folders = config.locations.values_list('location', flat=True)

            folder_query = ""
            for index, folder in enumerate(folders):
                cmis_folder = self._get_or_create_folder(folder, self._get_root_folder)
                folder_query += f"IN_TREE(D, '{cmis_folder.properties.get('cmis:objectId')}') "
                if index + 1 < len(folders):
                    folder_query += "OR "
            query = self.documents_query(folder_query)

        print(query)
        # Remove the /'s from the string
        query = codecs.escape_decode(query)[0].decode()
        print(query)

        result_set = self._get_repo.query(query)
        unpacked_result_set = [item for item in result_set]
        cmis_documents = [doc.getLatestVersion() for doc in unpacked_result_set]
        return cmis_documents

    def get_cmis_document(self, identificatie):
        """
        Given a cmis document instance.

        :param identificatie.
        :return: :class:`AtomPubDocument` object
        """
        query = self.document_query(identificatie)
        result_set = self._get_repo.query(query)
        unpacked_result_set = [item for item in result_set]
        if not unpacked_result_set:
            error_string = "Document met identificatie {} bestaat niet in het CMIS connection".format(identificatie)
            raise DocumentDoesNotExistError(error_string)

        doc = unpacked_result_set[0]
        doc = doc.getLatestVersion()
        return doc

    def update_document(self, identificatie, data, stream=None):
        cmis_doc = self.get_cmis_document(identificatie)

        # build up the properties
        current_properties = cmis_doc.properties
        new_properties = self._build_properties(identificatie, data)
        diff_properties = {
            key: value
            for key, value in new_properties.items()
            if current_properties.get(key) != new_properties.get(key)
        }

        print(diff_properties)  # TODO: remove print

        try:
            cmis_doc.updateProperties(diff_properties)
        except UpdateConflictException as exc:
            # Node locked!
            raise DocumentConflictException from exc

        if stream is not None:
            cmis_doc.setContentStream(stream, None)

    def update_case_connection(self, cmis_doc, data):
        current_properties = cmis_doc.properties
        new_properties = self._build_case_properties(data)
        diff_properties = {
            key: value
            for key, value in new_properties.items()
            if current_properties.get(key) != new_properties.get(key)
        }

        print(diff_properties)  # TODO: remove print

        try:
            cmis_doc.updateProperties(diff_properties)
        except UpdateConflictException as exc:
            # Node locked!
            raise DocumentConflictException from exc

    # Private functions.
    # TODO: Paste private functions.
    def _get_or_create_folder(self, name, parent, properties=None):
        """
        Get or create the folder with :param:`name` in :param:`parent`.

        :param name: string, the name of the folder to create.
        :param parent: parent folder to create the folder in as subfolder.
        :param properties: dictionary with cmis and/or custom properties to
          pass to the folder object
        :return: the folder that was retrieved or created.
        """
        print('===================================================')
        existing = next((child for child in parent.getChildren() if str(child.name) == str(name)), None)
        if existing is not None:
            return existing

        print(parent)
        print(name)
        return parent.createFolder(name, properties=properties or {})

    def _build_properties(self, identificatie, data):
        return {
            "cmis:objectTypeId": CMISObjectType.edc,  # Set the type of document that is uploaded.
            "cmis:name": data.get('titel'),
            "drc:identificatie": identificatie,
            "drc:bronorganisatie": data.get('bronorganisatie'),
            "drc:creatiedatum": data.get('creatiedatum'),
            "drc:vertrouwelijkaanduiding": data.get('vertrouwelijkaanduiding', ''),
            "drc:auteur": data.get('auteur'),
            "drc:status": data.get('status', ''),
            "drc:beschrijving": data.get('beschrijving', ''),
            "drc:ontvangstdatum": data.get('ontvangstdatum'),
            "drc:verzenddatum": data.get('verzenddatum'),
            "drc:indicatie_gebruiksrecht": data.get('indicatie_gebruiksrecht', ''),
            "drc:ondertekening_soort": data.get('ondertekening_soort', ''),
            "drc:ondertekening_datum": data.get('ondertekening_datum'),
            "drc:informatieobjecttype": data.get('informatieobjecttype', ''),
            "drc:formaat": data.get('formaat', ''),
            "drc:taal": data.get('taal'),
            "drc:bestandsnaam": data.get('bestandsnaam', ''),
            "drc:link": data.get('link', ''),
            "drc:integriteit_algoritme": data.get('integriteit_algoritme', ''),
            "drc:integriteit_waarde": data.get('integriteit_waarde', ''),
            "drc:integriteit_datum": data.get('integriteit_datum'),
        }

    def _build_case_properties(self, data):
        return {
            "drc:oio_zaak_url": data.get('object'),
            "drc:oio_object_type": data.get('objectType'),
            "drc:oio_aard_relatie_weergave": data.get('aardRelatieWeergave'),
            "drc:oio_titel": data.get('titel'),
            "drc:oio_beschrijving": data.get('beschrijving'),
            "drc:oio_registratiedatum": timezone.now().date(),
        }

    def _check_document_exists(self, identificatie):
        try:
            self.get_cmis_document(identificatie)
        except DocumentDoesNotExistError:
            pass
        else:
            error_string = "Document identificatie {} is niet uniek".format(identificatie)
            raise DocumentExistsError(error_string)

    # ! Not used yet.
    # ! Fix
    def get_folder_name(self, zaak_url, folder_config):
        name = ""
        if folder_config.type == CMISObjectType.zaak_folder:
            name = slugify(zaak_url)
        else:
            if not folder_config.name:
                raise ValueError(("Could not determine a folder name for zaak {}").format(slugify(zaak_url)))
        return folder_config.name or name

    def _get_zaakfolder(self, zaak_url):
        bits = [self.get_folder_name(zaak_url, folder_config) for folder_config in upload_to(zaak_url)]
        path = "/" + ("/").join(bits)
        return self._get_repo.getObjectByPath(path)

    def _build_cmis_doc_properties(self, connection, filename=None):
        properties = connection.get_cmis_properties()
        properties["cmis:objectTypeId"] = CMISObjectType.edc
        if filename is not None:
            properties["cmis:name"] = filename
        return properties

    def creeer_zaakfolder(self, zaak_url):
        """
        Maak de zaak folder aan in het DRC.

        :param zaak_url: Een link naar de zaak.
        :return: :class:`cmslib.atompub_binding.AtomPubFolder` object - de
          cmslib representatie van de (aangemaakte) zaakmap.
        """
        upload_to_folder = upload_to(zaak_url)
        for folder_config in upload_to_folder:
            if folder_config.type == CMISObjectType.zaken:
                folder_config.type = "cmis:folder"

        parent = None
        for folder_config in upload_to_folder:
            properties = {"cmis:objectTypeId": folder_config.type} if folder_config.type else {}
            name = self.get_folder_name(zaak_url, folder_config)
            parent, _ = self._get_or_create_folder(name, properties, parent=parent)

        zaak_folder = parent
        return zaak_folder

    def geef_inhoud(self, document):
        """
        Retrieve the document via its identifier from the DRC.

        :param document: EnkelvoudigInformatieObject instance
        :return: tuple of (filename, BytesIO()) with the stream filename and the binary content
        """
        try:
            doc = self.get_cmis_document(document)
        except DocumentDoesNotExistError:
            return (None, BytesIO())

        filename = doc.properties["cmis:name"]
        empty = doc.properties["cmis:contentStreamId"] is None
        if empty:
            return (filename, BytesIO())
        return (filename, doc.getContentStream())

    def relateer_aan_zaak(self, document, zaak_url):
        """
        Wijs het document aan :param:`zaak` toe.

        Verplaatst het document van de huidige folder naar de zaakfolder.
        """
        cmis_doc = self.get_cmis_document(document)
        zaakfolder = self._get_zaakfolder(zaak_url)
        parent = [parent for parent in cmis_doc.getObjectParents()][0]
        cmis_doc.move(parent, zaakfolder)

    def checkout(self, document):
        """
        Checkout (lock) the requested document and return the PWC ID + check out username.

        :param document: :class:`EnkelvoudigInformatieObject` instance.
        """
        cmis_doc = self.get_cmis_document(document)
        try:
            pwc = cmis_doc.checkout()
        except UpdateConflictException as exc:
            raise DocumentLockedException("Document was already checked out") from exc

        pwc.reload()
        checkout_id = pwc.properties["cmis:versionSeriesCheckedOutId"]
        checkout_by = pwc.properties["cmis:versionSeriesCheckedOutBy"]
        return (checkout_id, checkout_by)

    def cancel_checkout(self, document, checkout_id):
        cmis_doc = self.get_cmis_document(document, checkout_id=checkout_id)
        cmis_doc.cancelCheckout()

    def ontkoppel_zaakdocument(self, document, zaak_url):
        cmis_doc = self.get_cmis_document(document)
        cmis_folder = self._get_zaakfolder(zaak_url)
        trash_folder, _ = self._get_or_create_folder(self.TRASH_FOLDER)
        cmis_doc.move(cmis_folder, trash_folder)

    def gooi_in_prullenbak(self, document):
        cmis_doc = self.get_cmis_document(document)
        trash_folder, _ = self._get_or_create_folder(self.TRASH_FOLDER)
        default_folder, _ = self._get_or_create_folder(self.TEMP_FOLDER_NAME)
        cmis_doc.move(default_folder, trash_folder)

    def is_locked(self, document):
        cmis_doc = self.get_cmis_document(document)
        pwc = cmis_doc.getPrivateWorkingCopy()
        return pwc is not None

    def verwijder_document(self, document):
        cmis_doc = self.get_cmis_document(document)
        cmis_doc.delete()

cmis_client = CMISDRCClient()
