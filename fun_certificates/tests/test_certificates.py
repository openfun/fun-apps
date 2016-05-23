# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from certificates.models import GeneratedCertificate, CertificateStatuses, CertificateHtmlViewConfiguration
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from courses.tests.factories import CourseFactory as FunCourseFactory
from fun.tests.utils import skipUnlessLms

from ..utils import cert_id_encode, cert_id_decode, get_encoded_cert_id
from .helpers import HelperMethods

configuration = """{ "default":{ "accomplishment_class_append":"accomplishment-certificate", "platform_name":"Fun-MOOC", "company_about_url":"https://cargo.fun-mooc.fr/about", "company_privacy_url":"https://cargo.fun-mooc.fr/privacy", "company_tos_url":"https://cargo.fun-mooc.fr/tos", "company_verified_certificate_url":"http://www.YourOrganization.com/about_verified_certificates", "logo_src":"/static/funsite/images/logos/fun195.png", "logo_url":"https://cargo.fun-mooc.fr/" }, "honor":{ "certificate_type":"honor", "certificate_title":"Attestation", "document_body_class_append":"is-honorcode" }, "verified":{ "certificate_type":"verified", "certificate_title":"Certificat vérifié", "document_body_class_append":"is-idverified" }, "base":{ "certificate_type":"base", "certificate_title":"Certificate of Achievement", "document_body_class_append":"is-base" }, "distinguished":{ "certificate_type":"distinguished", "certificate_title":"Distinguished Certificate of Achievement", "document_body_class_append":"is-distinguished" } }"""


class CertURLEncodingTests(TestCase):

    def test_cert_id_encode(self):
        cert_id = 42
        key = 'test'
        encoded = cert_id_encode(key, cert_id)
        decoded = cert_id_decode(key, encoded)
        self.assertEqual(cert_id, decoded)


@skipUnlessLms
@override_settings(SECRET_KEY='test')
class ViewTests(ModuleStoreTestCase, HelperMethods):
    def setUp(self):
        super(ViewTests, self).setUp()
        self.course = CourseFactory(org='fun', course='course', number='0001',
                display_name=u"verified course", ispublic=True)
        ck = self.course.id
        self.fun_course = FunCourseFactory(key=unicode(ck))
        self.user = UserFactory(username='user1')  # user with profile

        # add certificate information to self.course
        self._add_course_certificates(count=1, signatory_count=3)

        CertificateHtmlViewConfiguration.objects.create(configuration=configuration, enabled=True)

        CourseEnrollmentFactory(course_id=self.course.id, user=self.user)
        self.certif = GeneratedCertificate.objects.create(user=self.user, course_id=ck,
            status=CertificateStatuses.downloadable,
            mode=GeneratedCertificate.MODES.verified)
        self.encoded = get_encoded_cert_id('test', unicode(self.course.id), self.user.id)

    def test_certif_valid(self):
        response = self.client.get(reverse('short-cert-url', args=[self.encoded]))
        self.assertEqual(200, response.status_code)

    def test_certif_not_passing(self):
        self.certif.status = CertificateStatuses.notpassing
        self.certif.save()
        response = self.client.get(reverse('short-cert-url', args=[self.encoded]))
        self.assertEqual(404, response.status_code)

    def test_certif_not_verified(self):
        self.certif.mode = 'honor'
        self.certif.save()
        response = self.client.get(reverse('short-cert-url', args=[self.encoded]))
        self.assertEqual(404, response.status_code)
