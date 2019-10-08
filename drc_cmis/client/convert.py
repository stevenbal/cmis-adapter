import base64
import logging
from datetime import datetime

from django.conf import settings
from django.urls import reverse

import iso8601

from .mapper import reverse_mapper

logger = logging.getLogger(__name__)


def to_date(value):
    tmp_datetime = parseDateTimeValue(value)
    if tmp_datetime:
        return tmp_datetime.date()
    return None


def parseDateTimeValue(value):
    """
    Utility function to return a datetime from a string.
    """
    if type(value) == str:
        return iso8601.parse_date(value)
    elif type(value) == int:
        return datetime.fromtimestamp(value / 1000)
    else:
        return None


def make_enkelvoudiginformatieobject_dataclass(cmis_doc, dataclass, skip_deleted=False):
    if cmis_doc.verwijderd and not skip_deleted:
        # Return None if document is deleted.
        return None

    path = reverse('enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_doc.versionSeriesId})
    url = f"{settings.HOST_URL}{path}"

    download_link = reverse(
        'enkelvoudiginformatieobjecten-download',
        kwargs={'version': '1', 'uuid': cmis_doc.versionSeriesId}
    )
    download_url = f"{settings.HOST_URL}{download_link}"

    return dataclass(
        url=url,
        inhoud=download_url,
        creatiedatum=to_date(cmis_doc.creatiedatum),
        ontvangstdatum=to_date(cmis_doc.ontvangstdatum),
        verzenddatum=to_date(cmis_doc.verzenddatum),
        integriteit_datum=to_date(cmis_doc.integriteit_datum),
        ondertekening_datum=to_date(cmis_doc.ondertekening_datum),
        titel=cmis_doc.titel,
        identificatie=cmis_doc.identificatie,
        bronorganisatie=cmis_doc.bronorganisatie,
        vertrouwelijkheidaanduiding=cmis_doc.vertrouwelijkheidaanduiding,
        auteur=cmis_doc.auteur,
        status=cmis_doc.status,
        beschrijving=cmis_doc.beschrijving,
        indicatie_gebruiksrecht=cmis_doc.indicatie_gebruiksrecht,
        ondertekening_soort=cmis_doc.ondertekening_soort,
        informatieobjecttype=cmis_doc.informatieobjecttype,
        formaat=cmis_doc.formaat,
        taal=cmis_doc.taal,
        bestandsnaam=cmis_doc.bestandsnaam,
        link=cmis_doc.link,
        integriteit_algoritme=cmis_doc.integriteit_algoritme,
        integriteit_waarde=cmis_doc.integriteit_waarde,
        bestandsomvang=cmis_doc.bestandsomvang,
        locked=bool(cmis_doc.versionSeriesCheckedOutId),
    )


def make_enkelvoudiginformatieobject_dataclass_old(cmis_doc, dataclass, skip_deleted=False):
    properties = cmis_doc.getProperties()

    if properties.get('drc:document__verwijderd') and not skip_deleted:
        # Return None if document is deleted.
        return None

    try:
        inhoud = base64.b64encode(cmis_doc.get_content_stream().read()).decode("utf-8")
    except AssertionError:
        return None
    else:
        logger.error(properties)
        cmis_id = properties.get("cmis:versionSeriesId").split("/")[-1]
        path = reverse('enkelvoudiginformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_id})
        url = f"{settings.HOST_URL}{path}"
        download_url = f"{settings.HOST_URL}{reverse('cmis:cmis_download', kwargs={'uuid': cmis_id})}"

        obj_dict = {reverse_mapper(key): value for key, value in properties.items() if reverse_mapper(key)}
        # remove verwijderd
        del obj_dict["verwijderd"]

        # Correct datetimes to dates
        for key, value in obj_dict.items():
            if isinstance(value, datetime):
                obj_dict[key] = value.date()

        # These values are not in alfresco
        obj_dict["url"] = url
        obj_dict["inhoud"] = download_url
        obj_dict["bestandsomvang"] = len(inhoud)
        return dataclass(**obj_dict)


def make_objectinformatieobject_dataclass(cmis_doc, dataclass, skip_deleted=False):
    if cmis_doc.verwijderd and not skip_deleted:
        # Return None if document is deleted.
        return None

    path = reverse('objectinformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_doc.versionSeriesId})
    url = f"{settings.HOST_URL}{path}"

    eio_path = reverse('objectinformatieobjecten-detail', kwargs={'version': '1', 'uuid': cmis_doc.versionSeriesId})
    eio_url = f"{settings.HOST_URL}{path}"

    return dataclass(
        url=url,
        informatieobject=cmis_doc.eio_url,
        object=cmis_doc.object,
        object_type=cmis_doc.object_type,
        aard_relatie=cmis_doc.aard_relatie,
        titel=cmis_doc.connectie__titel,
        beschrijving=cmis_doc.connectie__beschrijving,
        registratiedatum=cmis_doc.registratiedatum,
    )


def make_objectinformatieobject_dataclass_OLD(cmis_doc, dataclass):
    properties = cmis_doc.properties

    obj_dict = {
        reverse_mapper(key, "connection"): value
        for key, value in properties.items()
        if reverse_mapper(key, "connection")
    }

    oio_detail = reverse("objectinformatieobjecten-detail", kwargs={"version": "1", "uuid": cmis_doc.versionSeriesId})
    eio_detail = reverse(
        "enkelvoudiginformatieobjecten-detail",
        kwargs={"version": "1", "uuid": cmis_doc.versionSeriesId}
    )
    url = f"{settings.HOST_URL}{oio_detail}"
    eio_url = f"{settings.HOST_URL}{eio_detail}"

    obj_dict["url"] = url
    obj_dict["informatieobject"] = eio_url

    return dataclass(**obj_dict)
