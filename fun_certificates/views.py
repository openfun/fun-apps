# -*- coding: utf-8 -*-


from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404

from certificates.models import GeneratedCertificate, CertificateStatuses
from certificates.views import render_html_view

from .utils import cert_id_decode


def short_cert_url(request, encoded_cert_id):
    """Retrieve GeneratedCertificate from its encoded short id and returns
    edX's view content for it.

    We have changed the SECRET_KEY, we need to check its previous value to access previously generated short urls.
    """

    # check the current secret key
    cert_id = cert_id_decode(settings.SECRET_KEY, encoded_cert_id) or cert_id_decode("", encoded_cert_id)
    if cert_id is None:
        raise Http404

    cert = get_object_or_404(
        GeneratedCertificate,
         id=cert_id,
         status=CertificateStatuses.downloadable,
         mode=GeneratedCertificate.MODES.verified
    )

    return render_html_view(request, cert.user_id, unicode(cert.course_id))
