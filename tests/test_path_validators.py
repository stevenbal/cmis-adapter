from django.core.exceptions import ValidationError
from django.test import TestCase

from drc_cmis.models import CMISConfig
from drc_cmis.utils.folder import get_folder_structure
from drc_cmis.validators import (
    folder_path_validator,
    other_folder_path_validator,
    zaak_folder_path_validator,
)


class FolderStructureTests(TestCase):
    def test_leading_slash(self):
        result = get_folder_structure("/foo")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].folder_name, "foo")
        self.assertEqual(result[0].object_type, None)

    def test_trailing_slash(self):
        result = get_folder_structure("foo/")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].folder_name, "foo")
        self.assertEqual(result[0].object_type, None)

    def test_leading_and_trailing_slashes(self):
        result = get_folder_structure("/foo/")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].folder_name, "foo")
        self.assertEqual(result[0].object_type, None)

    def test_str_and_objecttype_path_element(self):
        result = get_folder_structure("/foo[bar]/")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].folder_name, "foo")
        self.assertEqual(result[0].object_type, "bar")

    def test_tpl_path_element(self):
        result = get_folder_structure("/{{ foo }}/")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].folder_name, "{{ foo }}")
        self.assertEqual(result[0].object_type, None)

    def test_tpl_and_object_type_path_element(self):
        result = get_folder_structure("/{{ foo }}[bar]/")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].folder_name, "{{ foo }}")
        self.assertEqual(result[0].object_type, "bar")

    def test_various_path_elements(self):
        result = get_folder_structure(
            "/folder1/folder2[x]/{{ folder3 }}/{{ folder4 }}[y]/"
        )

        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].folder_name, "folder1")
        self.assertEqual(result[0].object_type, None)

        self.assertEqual(result[1].folder_name, "folder2")
        self.assertEqual(result[1].object_type, "x")

        self.assertEqual(result[2].folder_name, "{{ folder3 }}")
        self.assertEqual(result[2].object_type, None)

        self.assertEqual(result[3].folder_name, "{{ folder4 }}")
        self.assertEqual(result[3].object_type, "y")

    def test_empty_folder(self):
        with self.assertRaises(ValidationError):
            self.assertRaises(get_folder_structure("/foo//bar/"))


class ZakenFolderPathValidatorTests(TestCase):
    def test_default_zaak_folder_path(self):
        try:
            zaak_folder_path_validator(
                CMISConfig._meta.get_field("zaak_folder_path").default
            )
        except ValidationError:
            self.fail("Validator should pass")

    def test_missing_required_folder(self):
        with self.assertRaises(ValidationError):
            zaak_folder_path_validator("/foo/{{ zaaktype }}/")

    def test_invalid_template_folder_folder(self):
        with self.assertRaises(ValidationError):
            zaak_folder_path_validator("/foo/{{ bar }}/")


class OtherFolderPathValidatorTests(TestCase):
    def test_default_other_folder_path(self):
        try:
            other_folder_path_validator(
                CMISConfig._meta.get_field("other_folder_path").default
            )
        except ValidationError:
            self.fail("Validator should pass")

    def test_invalid_template_folder_folder(self):
        with self.assertRaises(ValidationError):
            zaak_folder_path_validator("/foo/{{ bar }}/")
