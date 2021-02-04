=========
Changelog
=========

1.2.0 (2021-02-04)
------------------

This release fixes a number of bugs and adds some new functionality.

* Added setting to configure main repository ID
* Improved readability of logging statements for webservice calls
* Added a URL mapper to deal with URL-length limitations (#37)
* Fixed being able to update ``Gebruiksrechten`` resource
* Fixed missing filename extensions in CMIS requests (#40)

1.1.2 (2020-12-10)
------------------

Bugfix release

* Fixed missing unique-together validation on identificatie-bronorganisatie
* Fixed packaging, now Javascript is included
* Fixed file content extraction for Corsa DMS
* Fixed CMIS queries w/r to duplicate folders
* Switched CI from Travis to Github Actions

1.1.1 (2020-09-06)
------------------

* Fixed binary content uploads (such as PDFs) in SOAP binding (#24)
* Added more logging for all calls (#26)

1.1.0 (2020-08-26)
------------------

* Added configurable paths to be used in the DMS when adding documents.
* Added connection status in admin.
* Fixed code coverage report.
* Fixed minor Corsa compatibility issues.
* Fixed minor documentation issues.

1.0.0 (2020-08-25)
------------------

Version 1.0.0 is a major overhaul of the project to ensure stability and to
allow for easier integration of newer Documenten API versions. Thanks to the
municipality of Utrecht and the municipality of Súdwest-Fryslân who made this
effort possible.

* Added support for CMIS 1.0 SOAP bindings
* Major rewrite of the code to support multiple CMIS bindings
* Renamed from "GEMMA DRC-CMIS" (`gemma-drc-cmis`) to "Documenten API CMIS
  adapter" (`cmis-adapter`)
* Code repository was moved from `GemeenteUtrecht` to `open-zaak` and now lives
  under the maintenance of the Open Zaak project team.
* License changed from MIT (0.5.0) to EUPL 1.2

0.5.0 (2019-05-06)
------------------

Last release under the control of the municipality of Utrecht.

After it's initial release on PyPI on April 16, 2019, several minor and patch
versions were released. These releases went mostly undocumented and we refer to
https://github.com/open-zaak/cmis-adapter/releases for a complete list.
