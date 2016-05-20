# -*- coding: utf-8 -*-

from hashids import Hashids

from opaque_keys.edx.keys import CourseKey

from certificates.models import GeneratedCertificate


def cert_id_encode(key, cert_id):
    hashids = Hashids(salt=key)
    hashid = hashids.encode(int(cert_id))
    return hashid


def cert_id_decode(key, hashid):
    hashids = Hashids(salt=key)
    cert_id = hashids.decode(hashid)[0]
    return cert_id


def get_encoded_cert_id(key, course_id, user_id):
    cert = GeneratedCertificate.objects.get(course_id=CourseKey.from_string(course_id), user_id=user_id)
    return cert_id_encode(key, cert.id)
