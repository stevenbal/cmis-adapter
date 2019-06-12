import base64

from django.conf import settings
from django.urls import reverse


def create_dict_from_cmis_doc(cmis_doc):
    properties = cmis_doc.getProperties()

    # Values that need some parsing.
    creatiedatum = properties.get("drc:creatiedatum")
    if creatiedatum:
        creatiedatum = creatiedatum.date()

    ontvangstdatum = properties.get("drc:ontvangstdatum")
    if ontvangstdatum:
        ontvangstdatum = ontvangstdatum.date()

    verzenddatum = properties.get("drc:verzenddatum")
    if verzenddatum:
        verzenddatum = verzenddatum.date()

    ondertekening_datum = properties.get("drc:ondertekening_datum")
    if ondertekening_datum:
        ondertekening_datum = ondertekening_datum.date()

    integriteit_datum = properties.get("drc:integriteit_datum")
    if integriteit_datum:
        integriteit_datum = integriteit_datum.date()

    identificatie = properties.get("drc:identificatie")

    cmis_id = properties.get("cmis:versionSeriesId").split('/')[-1]

    try:
        inhoud = base64.b64encode(cmis_doc.getContentStream().read()).decode("utf-8")
    except AssertionError:
        return None
    else:
        url = "{}{}".format(settings.HOST_URL, reverse(
            'enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id}
        ))
        return {
            "url": url,
            "inhoud": url,
            "creatiedatum": creatiedatum,
            "ontvangstdatum": ontvangstdatum,
            "verzenddatum": verzenddatum,
            "integriteit_datum": integriteit_datum,
            "ondertekening_datum": ondertekening_datum,
            "titel": properties.get("cmis:name"),
            "identificatie": identificatie,
            "bronorganisatie": properties.get("drc:bronorganisatie"),
            "vertrouwelijkaanduiding": properties.get("drc:vertrouwelijkaanduiding"),
            "auteur": properties.get("drc:auteur"),
            "status": properties.get("drc:status"),
            "beschrijving": properties.get("drc:beschrijving"),
            "indicatie_gebruiksrecht": properties.get("drc:indicatie_gebruiksrecht"),
            "ondertekening_soort": properties.get("drc:ondertekening_soort"),
            "informatieobjecttype": properties.get("drc:informatieobjecttype"),
            "formaat": properties.get("drc:formaat"),
            "taal": properties.get("drc:taal"),
            "bestandsnaam": properties.get("drc:bestandsnaam"),
            "link": properties.get("drc:link"),
            "integriteit_algoritme": properties.get("drc:integriteit_algoritme"),
            "integriteit_waarde": properties.get("drc:integriteit_waarde"),
            "bestandsomvang": len(inhoud),
        }


def create_case_dict_from_cmis_doc(cmis_doc):
    properties = cmis_doc.getProperties()

    # Values that need some parsing.
    creatiedatum = properties.get("drc:creatiedatum")
    if creatiedatum:
        creatiedatum = creatiedatum.date()

    ontvangstdatum = properties.get("drc:ontvangstdatum")
    if ontvangstdatum:
        ontvangstdatum = ontvangstdatum.date()

    verzenddatum = properties.get("drc:verzenddatum")
    if verzenddatum:
        verzenddatum = verzenddatum.date()

    ondertekening_datum = properties.get("drc:ondertekening_datum")
    if ondertekening_datum:
        ondertekening_datum = ondertekening_datum.date()

    integriteit_datum = properties.get("drc:integriteit_datum")
    if integriteit_datum:
        integriteit_datum = integriteit_datum.date()

    properties.get("drc:identificatie")

    cmis_id = properties.get("cmis:versionSeriesId").split('/')[-1]

    url = "{}{}".format(settings.HOST_URL, reverse(
        'objectinformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id}
    ))
    eio_url = "{}{}".format(settings.HOST_URL, reverse(
        'enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id}
    ))

    return {
        "url": url,
        "informatieobject": eio_url,
        "object": properties.get('drc:oio_zaak_url'),
        "object_type": properties.get("drc:oio_object_type"),
        "aard_relatie_weergave": properties.get("drc:oio_aard_relatie_weergave"),
        "titel": properties.get("drc:oio_titel"),
        "beschrijving": properties.get("drc:oio_beschrijving"),
        "registratiedatum": properties.get("drc:oio_registratiedatum"),
    }
