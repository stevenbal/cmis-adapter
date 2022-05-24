from typing import Optional, TypeVar

ZaakFolder = TypeVar("ZaakFolder")


class RearrangeFilesOnDeleteMixin:
    _zaakfolder = None

    @property
    def zaakfolder(self) -> Optional["ZaakFolder"]:
        if not self._zaakfolder and self.zaak:
            self._zaakfolder = self.client.query(
                "zaak", lhs=["drc:zaak__url = '%s'"], rhs=[self.zaak]
            )[0]
        return self._zaakfolder

    def _reorganise_files(self) -> None:
        """Reorganise files in the DMS when a relation between a zaak and a document is broken

        When a document is related to a zaak, it is located in the zaak folder and has an OIO in the 'Related Data'
        folder. If the ZIO relating the zaak and the document is deleted, the OIO is deleted, and the document
        should not remain in the zaak folder. This is done as follows:

        1. If the document is NOT a copy (i.e. it's the original document), it should be moved to the default folder.
           If there are related gebruiksrechten, then they should also be moved.
        2. If the document IS a copy, then it should be deleted. Related gebruiksrechten should also be deleted.

        see issue #32 for more details.
        """
        document_to_unrelate = self._get_related_document()
        gebruiksrechten_file = self._get_gebruiksrechten()

        if document_to_unrelate and document_to_unrelate.kopie_van:
            document_to_unrelate.delete_object()
            if gebruiksrechten_file:
                gebruiksrechten_file.delete_object()
        else:
            default_folder = self.client.get_or_create_other_folder()
            document_to_unrelate.move_object(default_folder)
            if gebruiksrechten_file:
                default_related_data_folder = self.client.get_or_create_folder(
                    "Related data", default_folder
                )
                gebruiksrechten_file.move_object(default_related_data_folder)

    def delete_object(self) -> None:
        if self.object_type == "zaak":
            self._reorganise_files()

        super().delete_object()
